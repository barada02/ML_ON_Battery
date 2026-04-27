from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import joblib
import pandas as pd
import numpy as np
import os
# import tensorflow as tf # Uncomment when LSTM is ready
# from catboost import CatBoostRegressor # Uncomment when CatBoost is ready

app = FastAPI(title="Battery Health ML API")

# Enable CORS so the React app can talk to this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict this to your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define the expected incoming JSON format from React
class BatteryTelemetry(BaseModel):
    cycleIndex: float
    temperature: float
    dischargeTime: float
    maxTempReached: float
    minVoltageRecorded: float
    voltageDrop: float
    resistance: float

# --- MODEL LOADING ---
# For now, we will mock the model loads if the files don't exist yet,
# to prevent the server from crashing before you've downloaded the files.

def load_model_safely(path):
    if os.path.exists(path):
        return joblib.load(path)
    return None

# Load SoH Models (Track A)
rf_soh = load_model_safely('saved_models/rf_soh_model.pkl')
xgb_soh = load_model_safely('saved_models/xgb_soh_model.pkl')
lgbm_soh = load_model_safely('saved_models/lgbm_soh_model.pkl')

# Load RUL Models (Track B)
rf_rul = load_model_safely('saved_models/rf_rul_model.pkl')
xgb_rul = load_model_safely('saved_models/xgb_rul_model.pkl')
lgbm_rul = load_model_safely('saved_models/lgbm_rul_model.pkl')

# TODO: Add LSTM and CatBoost loading here when you are ready!

@app.post("/api/analyze")
async def analyze_battery(data: BatteryTelemetry):
    try:
        # 1. Prepare the exact features the ML models expect in order
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
            "rf": {"soh": 0, "rul": 0},
            "xgb": {"soh": 0, "rul": 0},
            "lgbm": {"soh": 0, "rul": 0}
        }

        # 2. Run Random Forest Predictions
        if rf_soh and rf_rul:
            results["rf"]["soh"] = round(float(rf_soh.predict(input_features)[0]), 2)
            results["rf"]["rul"] = int(rf_rul.predict(input_features)[0])
        
        # 3. Run XGBoost Predictions
        if xgb_soh and xgb_rul:
            results["xgb"]["soh"] = round(float(xgb_soh.predict(input_features)[0]), 2)
            results["xgb"]["rul"] = int(xgb_rul.predict(input_features)[0])

        # 4. Run LightGBM Predictions
        if lgbm_soh and lgbm_rul:
            results["lgbm"]["soh"] = round(float(lgbm_soh.predict(input_features)[0]), 2)
            results["lgbm"]["rul"] = int(lgbm_rul.predict(input_features)[0])

        # If models aren't found, return mock data just so the UI doesn't break
        if not rf_soh:
            base = 100 - (data.cycleIndex * 0.15) - (data.resistance * 500)
            soh = max(0, min(100, base))
            results = {
                "rf": {"soh": round(soh + 1.2, 1), "rul": int((soh - 70) * 1.5)},
                "xgb": {"soh": round(soh - 0.5, 1), "rul": int((soh - 70) * 1.4)},
                "lgbm": {"soh": round(soh + 0.3, 1), "rul": int((soh - 70) * 1.45)}
            }
            results["warning"] = "Models not found! Displaying mathematical simulation."

        return results

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health_check():
    return {"status": "ok", "message": "NASA Battery ML Server is running"}
