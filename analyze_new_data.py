
import pandas as pd
import os

file_path = 'Bills.xlsx'
if not os.path.exists(file_path):
    print(f"File {file_path} not found.")
else:
    try:
        df = pd.read_excel(file_path)
        print("--- Columns ---")
        print(df.columns.tolist())
        print("\n--- First 3 Rows ---")
        print(df.head(3))
        print("\n--- Info ---")
        print(df.info())
        print("\n--- Status Distribution ---")
        if 'Status' in df.columns:
            print(df['Status'].value_counts())
        elif 'status' in df.columns:
            print(df['status'].value_counts())
    except Exception as e:
        print(f"Error reading excel: {e}")
