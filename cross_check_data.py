
import pandas as pd

# Load datasets
scraped_df = pd.read_csv('data/indian_bills.csv')
new_df = pd.read_excel('Bills.xlsx')

# Filter Scraped Private Bills
private_scraped = scraped_df[scraped_df['type'] == 'Private']
print(f"Scraped Private Bills: {len(private_scraped)}")

if len(private_scraped) > 0:
    sample_private = private_scraped.head(5)['title'].tolist()
    print("Sample Private Titles:", sample_private)

    # Check existence in New Data
    # Normalize titles for matching (lower, strip)
    new_titles = new_df['Short Title'].astype(str).str.lower().str.strip().tolist()
    
    found_count = 0
    for title in sample_private:
        if title.lower().strip() in new_titles:
            print(f"Found: {title}")
            found_count += 1
        else:
            print(f"Not Found: {title}")
            
    print(f"Found {found_count} out of {len(sample_private)}")
else:
    print("No private bills in scraped data to check.")
