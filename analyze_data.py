
import pandas as pd
import os

csv_path = 'data/indian_bills.csv'
if not os.path.exists(csv_path):
    print("CSV not found.")
else:
    df = pd.read_csv(csv_path)
    print("--- Status Counts ---")
    print(df['status'].value_counts())
    
    print("\n--- Type Counts ---")
    print(df['type'].value_counts())

    print("\n--- Ministry Counts (Top 10) ---")
    print(df['ministry'].value_counts().head(10))
