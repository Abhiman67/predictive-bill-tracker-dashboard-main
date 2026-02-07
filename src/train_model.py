
import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score
from sklearn.preprocessing import OneHotEncoder

def train_model():
    print("Loading data...")
    df = pd.read_csv('data/bills_processed.csv')
    
    # 1. Define Target
    # Passed/Enacted = 1, Others = 0
    # Process script already normalized status but let's re-verify
    # Statuses: Assented, Passed -> 1
    # Lapsed, Withdrawn, Negatived -> 0
    # Pending -> Exclude from training (can't learn from incomplete) or treat as 0?
    # Better to exclude Pending for training to have clear outcomes.
    
    passed_statuses = ['Assented', 'Passed']
    failed_statuses = ['Lapsed', 'Withdrawn', 'Negatived']
    
    # Filter out Unknown/Pending for training
    df_train = df[df['status'].isin(passed_statuses + failed_statuses)].copy()
    
    df_train['target'] = df_train['status'].apply(lambda x: 1 if x in passed_statuses else 0)
    
    print(f"Target Distribution:\n{df_train['target'].value_counts()}")
    
    # 2. Features
    # Use: ministry, is_amendment, is_appropriation, is_finance, year
    
    # Handle missing values in Ministry
    df_train['ministry'] = df_train['ministry'].fillna('Unknown')
    
    # Top Ministries
    top_ministries = df_train['ministry'].value_counts().nlargest(20).index
    df_train['ministry_clean'] = df_train['ministry'].apply(lambda x: x if x in top_ministries else 'Other')
    
    # One-hot encode Ministry
    # Numeric features: is_amendment, is_appropriation, is_finance, year
    
    features = pd.get_dummies(df_train[['ministry_clean']], drop_first=True)
    numeric_features = df_train[['is_amendment', 'is_appropriation', 'is_finance', 'year']]
    
    X = pd.concat([features, numeric_features], axis=1)
    y = df_train['target']
    
    # 3. Split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # 4. Train
    print("Training Random Forest...")
    rf = RandomForestClassifier(n_estimators=100, random_state=42)
    rf.fit(X_train, y_train)
    
    # 5. Evaluate
    y_pred = rf.predict(X_test)
    print("--- Classification Report ---")
    print(classification_report(y_test, y_pred))
    print(f"Accuracy: {accuracy_score(y_test, y_pred):.2f}")
    
    # 6. Save
    print("Saving model and artifacts...")
    joblib.dump(rf, 'data/indian_bill_model.pkl')
    # Save columns to ensure alignment during inference
    joblib.dump(X.columns.tolist(), 'data/model_columns.pkl')
    print("Done.")

if __name__ == "__main__":
    train_model()
