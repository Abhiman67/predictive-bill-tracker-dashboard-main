# Indian Parliament Bill Tracker & Analytics

## 📖 Overview
The **Indian Parliament Bill Tracker** is an AI-powered legislative analytics dashboard designed to monitor and predict the outcomes of bills in the **Lok Sabha** and **Rajya Sabha**.

## 🚀 Key Features
- **Predictive AI**: Uses a dedicated Machine Learning model (Random Forest) to forecast the "Passage Probability" of any bill.
- **Interactive Dashboard**: Enter a Bill ID to instantly view its status, sponsor, and likelihood of becoming law.
- **Legislative Timeline**: Visualizes the journey of a bill from introduction to enactment or lapse.
- **Comprehensive Database**: Powered by over **3,500 bills** from the Lok Sabha secretariat (2000-Present).

---

## 🏗️ System Architecture

### 1. Data Layer (`data/`)
The system sources data from official records:
*   **Source**: Integrated `Bills.xlsx` (Official Lok Sabha Data) containing **3,563 records**.
*   **Processed Data**: `data/bills_processed.csv` holds the normalized dataset used for training, featuring columns like `ministry`, `year`, `is_money_bill`, and `status`.
*   *(Legacy)*: Also includes a custom scraper (`src/scraper.py`) for PRS India data.

### 2. Machine Learning Model (`src/train_model.py`)
A custom **Random Forest Classifier** replaces static heuristic rules.
*   **Target**: Predicts if a bill will be **Passed/Assented** (1) or **Lapsed/Withdrawn/Negatived** (0).
*   **Features**:
    *   **Ministry**: The sponsoring department (e.g., *Finance*, *Home Affairs*).
    *   **Year**: Captures increased legislative activity in certain years of a term.
    *   **Bill Type**: Inferred from title keywords (e.g., *Amendment*, *Appropriation*, *Finance*).
*   **Performance**: The model achieves **86% Accuracy** on the test set.

### 3. Application Layer (`src/app.py` & `src/data_fetch.py`)
*   **Streamlit UI**: A responsive web interface `http://localhost:8501`.
*   **Real-time Inference**: The app loads the trained model artifacts (`indian_bill_model.pkl`) to generate live predictions.
*   **Dynamic Fallbacks**: If ML inference is uncertain, it employs historical heuristics.

---

## 💻 Installation & Usage

### Prerequisites
- Python 3.8+
- Required packages: `streamlit`, `pandas`, `scikit-learn`, `plotly`, `openpyxl`.

### Setup
1.  **Clone/Navigate** to the project directory.
2.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
3.  **Run the Dashboard**:
    ```bash
    streamlit run src/app.py
    ```

### How to Use
1.  Open the dashboard in your browser.
2.  **Search**: Enter a Bill ID (e.g., `2001`, `3050`) from the dataset.
3.  **Analyze**:
    *   **Gauge Chart**: Shows the probability of passage (0-100%).
    *   **Timeline**: See when the bill was introduced and passed by each House.
    *   **Insights**: Read the AI-generated explanation for the score.

---

## 📂 Project Structure
```
├── Bills.xlsx               # Source Data (User Provided)
├── data/
│   ├── bills_processed.csv  # Cleaned dataset for ML
│   ├── indian_bills.csv     # (Legacy) Scraped dataset
│   ├── indian_bill_model.pkl # Trained Random Forest Model
│   └── model_columns.pkl    # Feature columns for inference
├── src/
│   ├── app.py               # Main Streamlit Dashboard Application
│   ├── data_fetch.py        # Data loading and preprocessing logic
│   ├── scraper.py           # (Utility) Web scraper for PRS India
│   └── train_model.py       # ML Training Pipeline
├── process_bills.py         # Script to convert Excel -> CSV
├── requirements.txt         # Project Dependencies
└── README.md                # Project documentation
```

## 📜 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing
Contributions are welcome! Please fork the repository and submit a pull request.