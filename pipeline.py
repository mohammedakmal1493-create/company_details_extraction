import re
import asyncio
import aiohttp
import time
import random
from bs4 import BeautifulSoup
from googlesearch import search          # ← CHANGED: replaced duckduckgo
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Company, EnrichmentStatus

EMAIL_REGEX = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
PHONE_REGEX = re.compile(r'(\+91[\-\s]?)?[6-9]\d{9}')  # ← CHANGED: Indian mobile format

# ← EXPANDED: more aggregator/spam domains blocked
DOMAIN_BLACKLIST = [
    'wikipedia.org', 'linkedin.com', 'facebook.com', 'indiamart.com',
    'justdial.com', 'youtube.com', 'netflix.com', 'chatgpt.com', 'openai.com',
    'twitter.com', 'instagram.com', 'amazon.com', 'flipkart.com',
    'zaubacorp.com', 'tofler.in', 'tracxn.com', 'crunchbase.com',
    'glassdoor.com', 'ambitionbox.com', 'sulekha.com', 'quora.com'
]

# ← REMOVED: clean_company_name_for_domain() — this was generating fake URLs, deleted entirely

def discover_website(company_name: str) -> str | None:
    """Search Google for the company's real website."""
    try:
        time.sleep(random.uniform(2.0, 4.0))  # ← INCREASED delay to avoid Google blocking
        query = f'"{company_name}" official website India'  # ← CHANGED: added quotes + India
        
        for url in search(query, num_results=5, lang="en"):  # ← CHANGED: googlesearch
            url_lower = url.lower()
            if not any(bad in url_lower for bad in DOMAIN_BLACKLIST):
                return url
    except Exception as e:
        print(f"Search error for {company_name}: {e}")
    return None  # ← Return None honestly, never a fake URL

async def fetch_html(session: aiohttp.ClientSession, url: str) -> str:
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=10),  # ← INCREASED timeout
                               headers=headers, allow_redirects=True) as response:
            if response.status == 200:
                return await response.text()
    except Exception:
        pass
    return ""

def parse_contact_info(html: str) -> tuple[set, set]:
    soup = BeautifulSoup(html, 'html.parser')
    text = soup.get_text()
    
    emails = set(EMAIL_REGEX.findall(text))
    phones = set(PHONE_REGEX.findall(text))
    
    # ← NEW: Filter out junk/system emails
    junk_prefixes = ('noreply', 'no-reply', 'donotreply', 'mailer', 'bounce', 'support@sentry')
    emails = {e for e in emails if not any(e.lower().startswith(j) for j in junk_prefixes)}
    
    return emails, phones

# ← NEW: Validate that the found website actually belongs to this company
def validate_website(company_name: str, html: str) -> bool:
    if not html:
        return False
    soup = BeautifulSoup(html, 'html.parser')
    page_text = soup.get_text().lower()
    
    # Strip legal suffixes to get core name keywords
    stop_words = {'private', 'limited', 'pvt', 'ltd', 'inc', 'and', 'the', 'of', '&'}
    keywords = [
        w.lower() for w in company_name.split()
        if w.lower() not in stop_words and len(w) > 2
    ]
    
    if not keywords:
        return True  # Can't validate, give benefit of doubt
    
    matches = sum(1 for kw in keywords if kw in page_text)
    return matches >= max(1, len(keywords) // 2)  # At least half keywords must appear

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
        try:
            async with aiohttp.ClientSession() as session:
                # ← NEW: Scrape homepage + contact page for better results
                pages_to_scrape = [
                    website,
                    website.rstrip('/') + '/contact',
                    website.rstrip('/') + '/contact-us',
                    website.rstrip('/') + '/about',
                ]
                
                homepage_html = await fetch_html(session, website)
                
                # ← NEW: Validate website actually belongs to this company
                if not validate_website(target_name, homepage_html):
                    print(f"Website {website} failed validation for {target_name}")
                    company.website = None
                    company.email = None
                    company.phone = None
                    company.enrichment_status = EnrichmentStatus.FAILED
                    db.commit()
                    db.close()
                    return
                
                company.website = website
                
                for url in pages_to_scrape:
                    html = await fetch_html(session, url)
                    if html:
                        emails, phones = parse_contact_info(html)
                        all_emails.update(emails)
                        all_phones.update(phones)
                        
        except Exception as e:
            print(f"Scraping error for {target_name}: {e}")

    else:
        # ← CHANGED: No website found → store NULL, mark FAILED (no more fake data!)
        print(f"No website found for: {target_name}")
        company.website = None
        company.email = None
        company.phone = None
        company.enrichment_status = EnrichmentStatus.FAILED
        db.commit()
        db.close()
        return

    # Store real data only
    company.email = ", ".join(list(all_emails)[:2]) if all_emails else None
    company.phone = ", ".join(list(all_phones)[:2]) if all_phones else None
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
        # ← CHANGED: Run 5 at a time (not all 100 at once) to avoid being blocked
        semaphore = asyncio.Semaphore(5)
        async def limited(cid):
            async with semaphore:
                await enrich_single_company(cid)
        tasks = [limited(c.id) for c in pending_companies]
        await asyncio.gather(*tasks)

    if pending_companies:
        asyncio.run(main())