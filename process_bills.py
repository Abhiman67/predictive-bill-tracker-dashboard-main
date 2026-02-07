
import pandas as pd
import numpy as np

def process_bills():
    print("Reading Bills.xlsx...")
    try:
        df = pd.read_excel('Bills.xlsx')
    except Exception as e:
        print(f"Error: {e}")
        return

    # Normalize Columns
    # Mapping:
    # 'Short Title' -> 'title'
    # 'Ministry' -> 'ministry'
    # 'Date of Introduction' -> 'introduction_date'
    # 'Status' -> 'status'
    # 'Bill Number' -> 'bill_id' (if unique) - checking duplicates later
    
    df = df.rename(columns={
        'Short Title': 'title',
        'Ministry': 'ministry',
        'Date of Introduction': 'introduction_date',
        'Status': 'status',
        'Bill Number': 'bill_id'
    })
    
    # Fill NAs
    df['ministry'] = df['ministry'].fillna('Unknown')
    df['status'] = df['status'].fillna('Unknown')
    
    # Standardize Status
    # Valid: Assented, Lapsed, Passed, Withdrawn, Pending, Negatived
    # We want to map these to: 
    # Passed -> Assented, Passed
    # Failed -> Lapsed, Withdrawn, Negatived
    # Pending -> Pending
    
    # Date Handling
    # '2025-01-30' format usually in Excel, or datetime objects
    df['introduction_date'] = pd.to_datetime(df['introduction_date'], errors='coerce')
    df['year'] = df['introduction_date'].dt.year.fillna(0).astype(int)
    
    # Feature Extraction from Title
    # 1. Type (Government vs Private)
    # Heuristic: If 'Private' not in title, assume Government (mostly true for this dataset)
    # But wait, did we see explicit private bills? 
    # The user said "Bills.xlsx", usually Lok Sabha secretariat data.
    # Let's extract "Amendment" status
    df['is_amendment'] = df['title'].str.contains('Amendment', case=False, na=False).astype(int)
    df['is_appropriation'] = df['title'].str.contains('Appropriation', case=False, na=False).astype(int)
    df['is_finance'] = df['title'].str.contains('Finance', case=False, na=False).astype(int)
    
    # Save
    output_path = 'data/bills_processed.csv'
    df.to_csv(output_path, index=False)
    print(f"Saved {len(df)} bills to {output_path}")
    print(df['status'].value_counts())

if __name__ == "__main__":
    process_bills()
