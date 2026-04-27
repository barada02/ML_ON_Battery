import os

# 1. SILENCE TENSORFLOW (Must be done before importing tf)
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

import uvicorn
import joblib
import pandas as pd
import numpy as np
import tensorflow as tf
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from catboost import CatBoostRegressor

# Initialize FastAPI
app = FastAPI(title="Battery Health ML API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount the UI directory for static files (CSS, JS)
app.mount("/ui", StaticFiles(directory="ui"), name="ui")

# Request Schema
class BatteryTelemetry(BaseModel):
    cycleIndex: float
    temperature: float
    dischargeTime: float
    maxTempReached: float
    minVoltageRecorded: float
    voltageDrop: float
    resistance: float

# Helper functions for loading
def load_pkl(path):
    if os.path.exists(path):
        print(f"Loading: {os.path.basename(path)}...")
        return joblib.load(path)
    print(f"--- Warning: Model NOT found at {path} ---")
    return None

def load_keras(path):
    if os.path.exists(path):
        print(f"Loading Keras Model: {os.path.basename(path)}...")
        return tf.keras.models.load_model(path)
    print(f"--- Warning: Keras Model NOT found at {path} ---")
    return None

# --- LOAD ALL MODELS ---
print("--- Initializing Model Loading ---")

# Paths (Using your specific absolute paths)
BASE_PATH = r'C:\Users\barad\Desktop\Kaggle\ML_ON_Battery\Model_Tr\saved_models'

# SoH Models
rf_soh = load_pkl(os.path.join(BASE_PATH, 'soh_models', 'rf_soh_model.pkl'))
xgb_soh = load_pkl(os.path.join(BASE_PATH, 'soh_models', 'xgb_soh_model.pkl'))
lgbm_soh = load_pkl(os.path.join(BASE_PATH, 'soh_models', 'lgbm_soh_model.pkl'))

# RUL Models
catboost_rul = load_pkl(os.path.join(BASE_PATH, 'Rul_Models', 'catboost_rul_model.pkl'))
lstm_rul = load_keras(os.path.join(BASE_PATH, 'Rul_Models', 'lstm_rul_model.keras'))
lstm_scaler = load_pkl(os.path.join(BASE_PATH, 'Rul_Models', 'lstm_scaler.pkl'))

print("--- All Models Loaded Successfully ---")

@app.get("/")
def read_root():
    return FileResponse("ui/index.html")

@app.post("/api/analyze")
async def analyze_battery(data: BatteryTelemetry):
    try:
        # Prepare input for Scikit-learn/XGB/CatBoost
        input_features = pd.DataFrame([{
            'Cycle_Index': data.cycleIndex,
            'Ambient_Temperature': data.temperature,
            'Discharge_Time_Seconds': data.dischargeTime,
            'Max_Temp_Reached': data.maxTempReached,
            'Min_Voltage_Recorded': data.minVoltageRecorded,
            'Voltage_Drop_Rate_V_per_sec': data.voltageDrop,
            'Internal_Resistance_Re': data.resistance
        }])

        results = {
            "soh": {
                "rf": 0.0,
                "xgb": 0.0,
                "lgbm": 0.0
            },
            "rul": {
                "catboost": 0,
                "lstm": 0
            }
        }

        # Calculate SoH (Multiply by 100 to convert to percentage if models output 0-1)
        # Note: If your models output raw Capacity (e.g. 1.8 Ah), you might want to divide by nominal capacity (like 2.0 Ah) then multiply by 100.
        # Assuming the model outputs fraction (0.0 to 1.0) based on your screenshot:
        if rf_soh:
            results["soh"]["rf"] = round(float(rf_soh.predict(input_features)[0]) * 100, 2)
        if xgb_soh:
            results["soh"]["xgb"] = round(float(xgb_soh.predict(input_features)[0]) * 100, 2)
        if lgbm_soh:
            results["soh"]["lgbm"] = round(float(lgbm_soh.predict(input_features)[0]) * 100, 2)

        # Calculate RUL
        if catboost_rul:
            results["rul"]["catboost"] = int(catboost_rul.predict(input_features)[0])
        
        if lstm_rul and lstm_scaler:
            scaled_features = lstm_scaler.transform(input_features)
            sequence = np.tile(scaled_features, (1, 10, 1)) 
            lstm_pred = lstm_rul.predict(sequence, verbose=0)
            results["rul"]["lstm"] = int(float(lstm_pred[0][0]))

        return results

    except Exception as e:
        print(f"Prediction Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ENTRY POINT
if __name__ == "__main__":
    print("Starting Uvicorn Server...")
    # Using the string "main:app" allows the 'reload' feature to work correctly
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)