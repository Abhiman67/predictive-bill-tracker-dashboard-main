# Indian Parliament Bill Tracker (Adaptation)

This project is a fork of the Predictive Bill Tracker, adapted to track and analyze legislation from the **Indian Parliament** (Lok Sabha & Rajya Sabha).

## 🇮🇳 Key Features
- **Data Source**: Scraped data from `prsindia.org`, covering bills from 2000-Present (approx. 950+ bills).
- **Metric Tracking**: Tracks bill status (Introduced, Passed Lok Sabha, Passed Rajya Sabha, Enacted/Assented).
- **Heuristic Prediction**: Uses bill type (Government vs. Private Member) and current progress to estimate passage probability.
- **Legislative Timeline**: Visualizes the journey of a bill through the houses.

## 📂 Project Structure
- `src/app.py`: Main Streamlit dashboard application.
- `src/data_fetch.py`: Handles data loading from `data/indian_bills.csv`.
- `src/scraper.py`: Python script to scrape the latest bill data from PRS India.
- `data/indian_bills.csv`: The local database of bills (CSV format).

## 🚀 How to Run
1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   pip install beautifulsoup4 requests
   ```
2. **Launch Dashboard**:
   ```bash
   streamlit run src/app.py
   ```

## 🔄 Updating Data
To fetch the latest bills from the web:
```bash
python3 src/scraper.py
```
This will crawl `prsindia.org/billtrack` and update `data/indian_bills.csv`. Note that scraping ~1000 bills takes about 10-15 minutes.

## ⚠️ Notes
- This is a prototype. The "Prediction" is based on logic, not a trained ML model, as structured historical training data is limited.
- "Sponsor" is mapped to "Ministry" for Government bills.
