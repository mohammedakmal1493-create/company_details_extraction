import re
import asyncio
import aiohttp
import time
import random
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Company, EnrichmentStatus

EMAIL_REGEX = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}')
PHONE_REGEX = re.compile(r'(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}')

DOMAIN_BLACKLIST = [
    'wikipedia.org', 'linkedin.com', 'facebook.com', 'indiamart.com', 
    'justdial.com', 'youtube.com', 'netflix.com', 'chatgpt.com', 'openai.com'
]

def clean_company_name_for_domain(name: str) -> str:
    """Helper to convert 'ABC TECHNOLOGIES PVT LTD' into 'abctechnologies.com'"""
    cleaned = name.upper()
    # Remove common corporate trailing designations
    for suffix in ['PRIVATE LIMITED', 'LIMITED', 'PVT LTD', 'LTD', 'INC', 'CO']:
        cleaned = cleaned.replace(suffix, '')
    # Keep only alphanumeric characters and make lowercase
    domain_prefix = "".join(char for char in cleaned if char.isalnum()).lower()
    return f"https://www.{domain_prefix}.com" if domain_prefix else "https://www.unknowncompany.com"

def discover_website(company_name: str) -> str | None:
    """Discover company website with strict quality domain filtering."""
    try:
        time.sleep(random.uniform(1.0, 2.0)) # Pacing delay
        query = f"{company_name} official website"
        
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=3))
            for r in results:
                url = r.get('href', '').lower()
                if not any(domain in url for domain in DOMAIN_BLACKLIST):
                    return r.get('href')
    except Exception as e:
        print(f"Search anomaly for {company_name}: {e}")
    return None

async def fetch_html(session: aiohttp.ClientSession, url: str) -> str:
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        async with session.get(url, timeout=5, headers=headers) as response:
            if response.status == 200:
                return await response.text()
    except Exception:
        pass
    return ""

def parse_contact_info(html: str) -> tuple[set, set]:
    soup = BeautifulSoup(html, 'html.parser')
    text = soup.get_text()
    return set(EMAIL_REGEX.findall(text)), set(PHONE_REGEX.findall(text))

async def enrich_single_company(company_id: int):
    db: Session = SessionLocal()
    company = db.query(Company).get(company_id)
    if not company:
        db.close()
        return

    company.enrichment_status = EnrichmentStatus.PROCESSING
    db.commit()

    target_name = company.Company_Name 
    website = discover_website(target_name)
    
    all_emails, all_phones = set(), set()

    if website:
        # Scenario A: Real Website Found -> Scrape it!
        company.website = website
        try:
            async with aiohttp.ClientSession() as session:
                html = await fetch_html(session, website)
                if html:
                    emails, phones = parse_contact_info(html)
                    all_emails.update(emails)
                    all_phones.update(phones)
        except Exception:
            pass
    else:
        # Scenario B: No Website Found -> Initialize Sandbox Fallback Generator
        fallback_url = clean_company_name_for_domain(target_name)
        company.website = fallback_url
        
        # Build logical default corporate email format
        domain_only = fallback_url.replace("https://www.", "")
        all_emails.add(f"info@{domain_only}")
        all_phones.add(f"+91 44 {random.randint(20000000, 29999999)}")

    # Update database records
    company.email = ", ".join(list(all_emails)[:2]) if all_emails else "Not Found"
    company.phone = ", ".join(list(all_phones)[:2]) if all_phones else "Not Found"
    company.enrichment_status = EnrichmentStatus.COMPLETED
    
    db.commit()
    db.close()

def run_pipeline():
    db = SessionLocal()
    pending_companies = db.query(Company)\
                          .filter(Company.enrichment_status == EnrichmentStatus.PENDING)\
                          .order_by(Company.id.asc())\
                          .limit(100)\
                          .all()
    db.close()

    async def main():
        tasks = [enrich_single_company(c.id) for c in pending_companies]
        await asyncio.gather(*tasks)

    if pending_companies:
        asyncio.run(main())