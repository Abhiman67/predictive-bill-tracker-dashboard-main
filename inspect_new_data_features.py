
import pandas as pd

df = pd.read_excel('Bills.xlsx')
print("--- First 5 Rows ---")
print(df.head(5)[['Short Title', 'Ministry', 'Date of Introduction', 'Status']])

print("\n--- Rows with Missing Ministry ---")
missing_ministry = df[df['Ministry'].isna()]
print(f"Count: {len(missing_ministry)}")
print(missing_ministry.head(5)[['Short Title', 'Status']])

print("\n--- Check for 'Private' in Title ---")
private_bills = df[df['Short Title'].str.contains('Private', case=False, na=False)]
print(f"Bills with 'Private' in title: {len(private_bills)}")
