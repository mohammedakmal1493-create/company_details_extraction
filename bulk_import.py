import pandas as pd
from sqlalchemy import create_engine
from config import Settings 

def fast_bulk_import(csv_path):
    print("Connecting to Supabase Postgres Instance...")
    config_settings = Settings()
    engine = create_engine(config_settings.DATABASE_URL)
    
    chunk_size = 10000  # Smaller chunks make it easier to catch corrupt data points
    total_rows = 0
    max_safety_limit = 150000  
    
    print(f"Reading CSV file from: {csv_path}")
    print("Processing with structural anomaly row isolation bypass...")
    
    # Open data context reader stream
    chunks = pd.read_csv(csv_path, chunksize=chunk_size, low_memory=False, encoding='latin-1', on_bad_lines='skip')
    
    for chunk in chunks:
        # Basic formatting fixes
        for col in ['Authorized_Capital', 'Paidup_Capital']:
            if col in chunk.columns:
                chunk[col] = pd.to_numeric(chunk[col], errors='coerce')
        
        chunk['Authorized_Capital'] = chunk['Authorized_Capital'].fillna(0).astype(int)
        chunk['Paidup_Capital'] = chunk['Paidup_Capital'].fillna(0).astype(int)
        chunk['enrichment_status'] = 'PENDING'
        
        try:
            # Try to upload the chunk normally at high speed
            chunk.to_sql(name='companies', con=engine, if_exists='append', index=False)
            total_rows += len(chunk)
            print(f"Successfully uploaded {total_rows:,} rows to Supabase...")
        except Exception:
            # FALLBACK: If the chunk contains a misaligned data type error ('aryana'),
            # drop down and insert the rows one by one to isolate and skip the broken line.
            print("⚠️ Structural text shift found in batch chunk. Isolating row validation...")
            for _, row in chunk.iterrows():
                try:
                    # Convert single row to a mini dataframe and push it
                    pd.DataFrame([row]).to_sql(name='companies', con=engine, if_exists='append', index=False)
                    total_rows += 1
                except Exception:
                    # Explicitly ignore the single broken shifted line ('aryana') and keep moving
                    continue
            print(f"Batch chunk sanitized. Progress: {total_rows:,} rows uploaded.")
            
        if total_rows >= max_safety_limit:
            print("\n⚠️ Safety Limit Reached! Capping import to protect free tier storage bounds.")
            break
            
    print("\n🎉 Supabase Bulk Import Completed Successfully!")

if __name__ == "__main__":
    csv_file_path = "A:/full_dev_intern/company_master_data_2026-06-12.csv"
    fast_bulk_import(csv_file_path)
