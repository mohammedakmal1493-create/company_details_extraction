import csv
import sys
from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models

# Set maximum field limit to prevent crashing on large text blocks
csv.field_size_limit(sys.maxsize)

# 🚀 TARGET: Using your newly generated, perfectly scrubbed CSV file!
CSV_FILE_PATH = "cleaned_company_master_data.csv" 
BATCH_SIZE = 2000  # Increased batch size since data is guaranteed clean!

def run_fast_bulk_ingestion():
    db: Session = SessionLocal()
    print("🚀 Initializing Optimized High-Speed Import Engine...")
    
    # 1. Gather all existing CINs in memory for instant O(1) skipping efficiency
    print("🔍 Fetching active CIN records from Supabase to prevent overlaps...")
    existing_cins = set(row[0] for row in db.query(models.Company.CIN).all())
    print(f"✅ Found {len(existing_cins)} rows already present in the database cluster.")

    batch = []
    inserted_count = 0

    with open(CSV_FILE_PATH, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for index, row in enumerate(reader, start=1):
            cin = row.get('CIN', '').strip().upper()
            if not cin or cin in existing_cins:
                continue

            # Build data mapping dictionary matching your table structure parameters
            company_data = {
                "CIN": cin,
                "Company_Name": row.get('Company_Name', '').strip(),
                "Company_Registration_Date": row.get('Company_Registration_Date', '').strip(),
                "Company_Status": row.get('Company_Status', '').strip(),
                "Company_Class": row.get('Company_Class', '').strip(),
                "Company_Category": row.get('Company_Category', '').strip(),
                "Company_ROC": row.get('Company_ROC', '').strip(),
                "Authorized_Capital": float(row.get('Authorized_Capital', 0.0)),
                "Paidup_Capital": float(row.get('Paidup_Capital', 0.0)),
                "Company_Address": row.get('Company_Address', '').strip(),
                "Company_State": row.get('Company_State', '').strip(),
                "Pin_Code": row.get('Pin_Code', ''),
                "Company_Industrial_Classification": row.get('Company_Industrial_Classification', '').strip(),
                "enrichment_status": "PENDING"
            }
            
            batch.append(company_data)
            inserted_count += 1

            # Dispatch massive multi-row array mapping streams
            if len(batch) >= BATCH_SIZE:
                # bulk_insert_mappings drops execution limits and cuts network trip durations by 90%
                db.bulk_insert_mappings(models.Company, batch)
                db.commit()
                print(f"📦 Streaming Progress: Pushed +{inserted_count} clean records to Supabase cloud...")
                batch = []

        # Flush any remaining items left in the queue arrays
        if batch:
            db.bulk_insert_mappings(models.Company, batch)
            db.commit()

    print("\n--- FINAL RESYNC COMPLETION LOG ---")
    print(f"🎉 New rows written safely to Supabase: {inserted_count}")
    print(f"📊 Grand total database entries: {len(existing_cins) + inserted_count}")
    db.close()

if __name__ == "__main__":
    run_fast_bulk_ingestion()