
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import re
from concurrent.futures import ThreadPoolExecutor, as_completed


BASE_URL = "https://prsindia.org"
Tracking_URL = "https://prsindia.org/billtrack"

def get_soup(url):
    try:
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        if response.status_code == 200:
            return BeautifulSoup(response.content, 'html.parser')
    except Exception as e:
        print(f"Error fetching {url}: {e}")
    return None

def fetch_all_bill_links():
    print(f"Fetching bill list from {Tracking_URL}...")
    soup = get_soup(Tracking_URL)
    if not soup:
        return []
    
    bill_links = []
    # Find all links that look like bill pages. 
    # Examining the site, they are usually in div.views-row or similar containers
    # We'll look for any anchor href identifying as /billtrack/bill-name
    
    for a in soup.find_all('a', href=True):
        href = a['href']
        if href.startswith('/billtrack/') and len(href.split('/')) == 3:
            full_url = BASE_URL + href
            if full_url not in bill_links:
                bill_links.append(full_url)
    
    # Remove duplicates and filtered pages if any
    bill_links = list(set(bill_links))
    print(f"Found {len(bill_links)} unique bill links.")
    return bill_links


def extract_bill_details(url):
    soup = get_soup(url)
    if not soup:
        return None

    detail = {
        'url': url,
        'title': 'Unknown',
        'ministry': '',
        'status': 'Unknown',
        'house': 'Unknown',
        'introduction_date': None,
        'passed_ls': None,
        'passed_rs': None,
        'assent_date': None,
        'type': 'Government',
        'short_title': 'Unknown'
    }

    # 1. Title
    h1 = soup.find('h1', class_='page-header')
    if not h1:
        h1 = soup.find('h1')
    
    if h1:
        detail['title'] = h1.get_text(strip=True)
    else:
        # Fallback to h2 > a with specific classes seen in inspection
        # <h2 class="mt-0 mb-1"><a class="active fs-28" ...>Title</a></h2>
        h2 = soup.find('h2', class_='mt-0 mb-1')
        if h2:
            detail['title'] = h2.get_text(strip=True)
        else:
             # Last resort: Try finding the active link that matches the url slug if possible, or just specific class
             a_title = soup.find('a', class_='fs-28')
             if a_title:
                 detail['title'] = a_title.get_text(strip=True)

    if detail['title'] != 'Unknown':
        detail['short_title'] = detail['title'].split(',')[0]
        if "Private Member" in detail['title']:
            detail['type'] = "Private"


    # 2. Ministry
    # div.field-name-field-ministry .field-item
    ministry_div = soup.find('div', class_='field-name-field-ministry')
    if ministry_div:
        item = ministry_div.find('div', class_='field-item')
        if item:
            detail['ministry'] = item.get_text(strip=True)

    # 3. Introduction Date
    # div.field-name-field-introduction-date .date-display-single
    intro_date_div = soup.find('div', class_='field-name-field-introduction-date')
    if intro_date_div:
        date_span = intro_date_div.find('span', class_='date-display-single')
        if date_span:
             detail['introduction_date'] = date_span.get_text(strip=True) # Keep format for now, e.g. "Aug 08, 2024"

    # 4. Intro House
    # Try multiple class variants
    intro_house_div = soup.find('div', class_=re.compile('field-name-field-intro.*house'))
    if intro_house_div:
        item = intro_house_div.find('div', class_='field-item')
        if item:
            detail['house'] = item.get_text(strip=True)
            
    # Fallback for House from Category/Text
    text_content = soup.get_text()
    if detail['house'] == 'Unknown':
        if "Lok Sabha" in text_content and "Rajya Sabha" not in text_content:
             detail['house'] = "Lok Sabha"
        elif "Rajya Sabha" in text_content and "Lok Sabha" not in text_content:
             detail['house'] = "Rajya Sabha"
        elif "Lok Sabha" in text_content: # Default to LS if both mentions or ambiguous
             detail['house'] = "Lok Sabha" 

    # 5. Bill Type (Category)
    # div.field-name-field-category
    category_div = soup.find('div', class_='field-name-field-category')
    if category_div:
        item = category_div.find('div', class_='field-item')
        if item:
            cat_text = item.get_text(strip=True)
            if "Private" in cat_text:
                detail['type'] = "Private"
            else:
                detail['type'] = "Government"
    
    # Fallback for Type
    if detail['type'] == 'Government': # Only check fallback if default
        if "Private Member" in text_content or "Private Member" in detail['title']:
            detail['type'] = "Private"

    

    # 5. Status Dates
    # Passed LS
    pass_ls_div = soup.find('div', class_='field-name-field-passed-lok-sabha')
    if pass_ls_div:
        date_span = pass_ls_div.find('span', class_='date-display-single')
        if date_span:
            detail['passed_ls'] = date_span.get_text(strip=True)

    # Passed RS
    pass_rs_div = soup.find('div', class_='field-name-field-passed-rajya-sabha')
    if pass_rs_div:
        date_span = pass_rs_div.find('span', class_='date-display-single')
        if date_span:
             detail['passed_rs'] = date_span.get_text(strip=True)

    # Assent
    assent_div = soup.find('div', class_='field-name-field-assent-date')
    if assent_div:
        date_span = assent_div.find('span', class_='date-display-single')
        if date_span:
             detail['assent_date'] = date_span.get_text(strip=True)

    # 6. Determine Status
    # Priority: Enacted > Passed > Passed One House > Introduced > Withdrawn
    
    # Check text content for fallbacks if fields recall failed
    text_content = soup.get_text()
    
    if detail['assent_date']:
        detail['status'] = "Enacted"
    elif detail['passed_ls'] and detail['passed_rs']:
        detail['status'] = "Passed"
    elif detail['passed_ls'] or detail['passed_rs']:
        detail['status'] = "Passed One House"
    elif "Assented" in text_content or "Act, 20" in detail['title']: # simplistic check for Act
         detail['status'] = "Enacted"
    elif "Passed" in text_content and "Lok Sabha" in text_content and "Passed" in text_content and "Rajya Sabha" in text_content:
         detail['status'] = "Passed"
    elif ("Passed" in text_content and "Lok Sabha" in text_content) or ("Passed" in text_content and "Rajya Sabha" in text_content):
         detail['status'] = "Pending" # Passed one house
    elif "Withdrawn" in text_content:
         detail['status'] = "Withdrawn"
    elif detail['introduction_date']:
        detail['status'] = "Introduced"
    elif "Introduced" in text_content:
        detail['status'] = "Introduced"
        
    return detail



def scrape_bill_safe(link):
    try:
        # random sleep to be polite even with threads, but shorter
        return extract_bill_details(link)
    except Exception as e:
        print(f"Error scraping {link}: {e}")
        return None

def scrape_bills(limit=None):
    links = fetch_all_bill_links()
    if limit:
        links = links[:limit]
    
    data = []
    print(f"Scraping {len(links)} bills with threading...")
    
    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(scrape_bill_safe, url): url for url in links}
        
        for i, future in enumerate(as_completed(future_to_url)):
            url = future_to_url[future]
            try:
                info = future.result()
                if info:
                    info['bill_id'] = 1000 + i 
                    data.append(info)
                if i % 50 == 0:
                    print(f"Processed {i}/{len(links)} bills...")
            except Exception as e:
                print(f"Generated an exception: {e}")
                
    df = pd.DataFrame(data)
    
    # Post-processing to match schema
    # bill_id,title,short_title,ministry,type,status,introduction_date,house,passed_ls,passed_rs,assent_date,total_actions
    
    # We should parse date format from "Aug 08, 2024" to "2024-08-08" for compatibility with dashboard
    for col in ['introduction_date', 'passed_ls', 'passed_rs', 'assent_date']:
        df[col] = pd.to_datetime(df[col], errors='coerce').dt.strftime('%Y-%m-%d')

    df['total_actions'] = df.apply(lambda x: 10 if x['status'] == 'Enacted' else 5, axis=1) # Mocked
    
    # Save
    output_path = 'data/indian_bills.csv'
    df.to_csv(output_path, index=False)
    print(f"Saved {len(df)} bills to {output_path}")

if __name__ == "__main__":
    # Scrape all bills with threading
    scrape_bills(limit=None)
  
 
