import pandas as pd
import numpy as np
import os
from datetime import datetime

# Path to the local CSV file
DATA_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'bills_processed.csv')

def load_indian_bills():
    """
    Load the Indian bills dataset from local CSV
    """
    if not os.path.exists(DATA_FILE):
        return pd.DataFrame()
    df = pd.read_csv(DATA_FILE)
    # Parse dates
    date_cols = ['introduction_date']
    for col in date_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')
    return df

def fetch_bill(bill_id, congress=None, bill_type=None):
    """
    Simulate fetching bill details by looking up the CSV
    """
    df = load_indian_bills()
    if df.empty:
        return pd.DataFrame()
    
    # Filter by bill_id (assuming simple integer matching for this prototype)
    # In a real app, logic would be more complex
    try:
        bill_row = df[df['bill_id'].astype(str) == str(bill_id)]
    except:
        return pd.DataFrame()

    if bill_row.empty:
        return pd.DataFrame()

    # Map CSV columns to the structure expected by app.py
    # This maintains compatibility without rewriting the whole app logic immediately
    # Map processed CSV columns to app structure
    # processed: title, ministry, introduction_date, status, bill_id, year, is_amendment, ...
    
    # Handle missing short_title
    title = bill_row['title'].values[0]
    short_title = title.split(',')[0] if ',' in str(title) else title

    mapped_data = {
        'title': title,
        'short_title': short_title,
        'bill_id': str(bill_id),
        'sponsor': bill_row['ministry'].values[0],
        'introduced_date': bill_row['introduction_date'].values[0],
        'status': bill_row['status'].values[0],
        'summary': "No summary available for this bill.",
        'congress': bill_row['year'].values[0], 
        'bill_type': "Government" if "Private" not in str(title) else "Private",
        # New ML features
        'year': bill_row['year'].values[0],
        'ministry': bill_row['ministry'].values[0],
        'is_amendment': bill_row['is_amendment'].values[0],
        'is_appropriation': bill_row['is_appropriation'].values[0],
        'is_finance': bill_row['is_finance'].values[0],
        # Mock old fields
        'house': 'Lok Sabha', # Default to LS for this dataset
        'type': "Government" if "Private" not in str(title) else "Private",
        'cosponsor_count': 0,
        'committees': 'None',
        'policy_area': bill_row['ministry'].values[0],
        'is_bipartisan': True,
        'sponsors': bill_row['ministry'].values[0],
        'sponsor_parties': 'Government',
        'dem_sponsors': 1,
        'rep_sponsors': 0
    }
    
    return pd.DataFrame([mapped_data])

def fetch_bill_actions(bill_id, congress=None, bill_type=None):
    """
    Generate mock actions based on the bill status to populate the timeline
    """
    df = load_indian_bills()
    if df.empty:
        return pd.DataFrame()
        
    try:
        bill_row = df[df['bill_id'].astype(str) == str(bill_id)].iloc[0]
    except:
        return pd.DataFrame()

    actions = []
    
    # 1. Introduction
    intro_date = bill_row['introduction_date']
    if pd.isna(intro_date):
        intro_date = f"{int(bill_row['year'])}-01-01" # Fallback

    actions.append({
        'date': intro_date,
        'text': "Introduced in Lok Sabha",
        'action_code': 'intro'
    })
    
    status = str(bill_row['status'])
    
    # 2. Status-based Actions
    if status in ['Passed', 'Assented']:
        actions.append({
            'date': intro_date, # Mock: same year
            'text': "Passed Lok Sabha",
            'action_code': 'passed_ls'
        })
        actions.append({
            'date': intro_date, # Mock
            'text': "Passed Rajya Sabha",
            'action_code': 'passed_rs'
        })
        
    if status == 'Assented':
        actions.append({
             'date': intro_date, # Mock
             'text': "Received Presidential Assent (Became Law)",
             'action_code': 'assent'
        })
        
    if status == 'Lapsed':
        actions.append({
             'date': intro_date,
             'text': "Bill Lapsed",
             'action_code': 'lapsed'
        })
        
    if status == 'Withdrawn':
        actions.append({
             'date': intro_date,
             'text': "Bill Withdrawn",
             'action_code': 'withdrawn'
        })
    
    return pd.DataFrame(actions)

def fetch_comprehensive_bill_data(bill_input, congress=None, bill_type=None):
    """
    Orchestrator function compatible with app.py
    """
    bill_df = fetch_bill(bill_input)
    if bill_df.empty:
        return None
        
    actions_df = fetch_bill_actions(bill_input)
    
    # Return structure matching what app.py expects
    return {
        'bill_info': bill_df,
        'actions': actions_df,
        'cosponsors': pd.DataFrame({'name': []}), 
        'subjects': {'subjects': ['Governance'], 'policy_area': bill_df['policy_area'].values[0]},
        'metrics': {
            'total_actions': len(actions_df),
            'committee_count': 0,
            'bipartisan_score': 0.0
        }
    }

if __name__ == "__main__":
    print(load_indian_bills())