# 🔋 NASA Battery ML Dashboard & Inference API

Predicting **State of Health (SoH)** and **Remaining Useful Life (RUL)** of Li-Ion Batteries using Machine Learning.

## 📊 1. Data Source & Engineering
The primary dataset used in this project is the **Lithium-Ion Battery Dataset from NASA PCoE**.

- **Source:** [Kaggle Dataset Link](https://www.kaggle.com/datasets/ckskaggle/li-ion-battery-dataset-from-nasa-pcoe/data)
- **EDA & Data Engineering (DE):** All exploratory data analysis and feature engineering were performed in the `EDA/eda-de.ipynb` notebook.
- **Generated Datasets:** The data engineering process generates the cleaned and feature-engineered CSV files located in the `csv_exports/` directory:
  - `ML_Engineered_Battery_Dataset.csv` (Targeted for SoH modeling)
  - `ML_Engineered_Battery_Dataset_RUL.csv` (Targeted for RUL modeling)

## 🧠 2. Model Training
All machine learning models were primarily trained on Kaggle to leverage cloud compute (though the notebooks are fully capable of being executed locally using the exported CSV files). 

The training pipeline is split across two core notebooks located in the `Model_Tr/` directory:
- **SoH Models Notebook** (`A-soh-models.ipynb`): Trains models to predict the current State of Health percentage using **Random Forest**, **XGBoost**, and **LightGBM**.
- **RUL Models Notebook** (`B-rul-models.ipynb`): Trains sequential and tree-based models to predict Remaining Useful Life (cycles remaining) using **CatBoost** and **LSTM Neural Networks**.

*The trained models are serialized and saved in the `Model_Tr/saved_models/` directory for fast inference loading.*

## 🚀 3. Inference API & UI Dashboard
We provide a unified **FastAPI** backend that simultaneously serves the machine learning inference endpoint and a beautifully integrated web UI Dashboard to test the models in real-time.

### How to Run Locally
1. **Activate your environment** and ensure all requirements are installed (e.g., `fastapi`, `uvicorn`, `tensorflow`, `catboost`, `xgboost`, `lightgbm`, `scikit-learn`).
2. **Navigate to the FastAPI directory:**
   ```bash
   cd FastApi
   ```
3. **Start the Uvicorn Server:**
   ```bash
   uvicorn main:app --reload
   ```
4. **Access the Dashboard:** Open your web browser and navigate to **[http://localhost:8000/](http://localhost:8000/)**. 

From the dashboard, you can input battery telemetry metrics (Cycle Index, Ambient Temp, Discharge Time, Voltage Drop, Internal Resistance, etc.) and instantly receive a side-by-side comparison of predictions from all 5 trained models.

## 📂 Project Structure Overview
```text
ML_ON_Battery/
├── Battery_DataSet/     # Raw NASA Battery Data files (.mat, .txt)
├── EDA/                 # Exploratory Data Analysis & Feature Engineering
├── csv_exports/         # Cleaned & Engineered CSV datasets ready for Training
├── Model_Tr/            # Training Notebooks (SoH & RUL) and Saved Models (.pkl, .keras)
├── FastApi/             # FastAPI Inference Server & Integrated UI Dashboard
│   ├── main.py          # API Endpoint & Model Loading logic
│   └── ui/              # HTML/CSS/JS for the Browser Dashboard
└── Battery_Dashboard/   # (Deprecated) Old standalone React Frontend
```