import sys
import pandas as pd
from sqlalchemy import create_engine
from config import settings

def fast_bulk_import(csv_path):
    print("Connecting to MySQL Database...")
    engine = create_engine(settings.DATABASE_URL)
    
    print(f"Reading CSV file from: {csv_path}")
    print("Processing in high-speed memory chunks of 100,000 rows...")
    
    chunk_size = 100000
    total_rows = 0
    
    try:
        # ADDED encoding='latin-1' HERE TO BYPASS UNICODE DECODE ERRORS
        for chunk in pd.read_csv(csv_path, chunksize=chunk_size, low_memory=False, encoding='latin-1'):
            chunk['enrichment_status'] = 'PENDING'
            
            chunk.to_sql(
                name='companies', 
                con=engine, 
                if_exists='append', 
                index=False,
                method='multi'
            )
            total_rows += len(chunk)
            print(f"Successfully uploaded {total_rows:,} rows...")

        print("\n🎉 Bulk Import Completed Successfully!")
        
    except Exception as e:
        print(f"\n❌ AN ERROR OCCURRED DURING IMPORT: {e}")

if __name__ == "__main__":
    csv_file_path = "A:/full_dev_intern/company_master_data_2026-06-12.csv"
    fast_bulk_import(csv_file_path)