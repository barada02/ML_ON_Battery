from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import joblib
import pandas as pd
import numpy as np
import os
import tensorflow as tf
from catboost import CatBoostRegressor

app = FastAPI(title="Battery Health ML API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class BatteryTelemetry(BaseModel):
    cycleIndex: float
    temperature: float
    dischargeTime: float
    maxTempReached: float
    minVoltageRecorded: float
    voltageDrop: float
    resistance: float

def load_pkl(path):
    if os.path.exists(path):
        return joblib.load(path)
    print(f"Warning: Model not found at {path}")
    return None

def load_keras(path):
    if os.path.exists(path):
        return tf.keras.models.load_model(path)
    print(f"Warning: Model not found at {path}")
    return None

# Load SoH Models (Track A)
rf_soh = load_pkl(r'C:\Users\barad\Desktop\Kaggle\ML_ON_Battery\Model_Tr\saved_models\soh_models\rf_soh_model.pkl')
xgb_soh = load_pkl(r'C:\Users\barad\Desktop\Kaggle\ML_ON_Battery\Model_Tr\saved_models\soh_models\xgb_soh_model.pkl')
lgbm_soh = load_pkl(r'C:\Users\barad\Desktop\Kaggle\ML_ON_Battery\Model_Tr\saved_models\soh_models\lgbm_soh_model.pkl')

# Load RUL Models (Track B)
catboost_rul = load_pkl(r'C:\Users\barad\Desktop\Kaggle\ML_ON_Battery\Model_Tr\saved_models\Rul_Models\catboost_rul_model.pkl')
lstm_rul = load_keras(r'C:\Users\barad\Desktop\Kaggle\ML_ON_Battery\Model_Tr\saved_models\Rul_Models\lstm_rul_model.keras')
lstm_scaler = load_pkl(r'C:\Users\barad\Desktop\Kaggle\ML_ON_Battery\Model_Tr\saved_models\Rul_Models\lstm_scaler.pkl')

@app.post("/api/analyze")
async def analyze_battery(data: BatteryTelemetry):
    try:
        input_features = pd.DataFrame([{
            'Cycle_Index': data.cycleIndex,
            'Ambient_Temperature': data.temperature,
            'Discharge_Time_Seconds': data.dischargeTime,
            'Max_Temp_Reached': data.maxTempReached,
            'Min_Voltage_Recorded': data.minVoltageRecorded,
            'Voltage_Drop_Rate_V_per_sec': data.voltageDrop,
            'Internal_Resistance_Re': data.resistance
        }])

        # Default fallback values
        results = {
            "rf": {"soh": 0, "rul": 0, "rul_model_name": "CatBoost"},
            "xgb": {"soh": 0, "rul": 0, "rul_model_name": "LSTM Network"},
            "lgbm": {"soh": 0, "rul": 0, "rul_model_name": "CatBoost"}
        }

        # Card 1: Random Forest SoH + CatBoost RUL
        if rf_soh and catboost_rul:
            results["rf"]["soh"] = round(float(rf_soh.predict(input_features)[0]), 2)
            results["rf"]["rul"] = int(catboost_rul.predict(input_features)[0])
        
        # Card 2: XGBoost SoH + LSTM RUL
        if xgb_soh and lstm_rul and lstm_scaler:
            results["xgb"]["soh"] = round(float(xgb_soh.predict(input_features)[0]), 2)
            
            # LSTM needs scaled data and sequence length of 10.
            # We replicate this single reading 10 times to simulate the required sequence.
            scaled_features = lstm_scaler.transform(input_features)
            sequence = np.tile(scaled_features, (10, 1)) # Shape (10, 7)
            sequence = np.expand_dims(sequence, axis=0)  # Shape (1, 10, 7)
            
            lstm_pred = lstm_rul.predict(sequence, verbose=0)
            results["xgb"]["rul"] = int(float(lstm_pred[0][0]))

        # Card 3: LightGBM SoH + CatBoost RUL (Re-using CatBoost for the 3rd card since we only have 2 RUL models)
        if lgbm_soh and catboost_rul:
            results["lgbm"]["soh"] = round(float(lgbm_soh.predict(input_features)[0]), 2)
            results["lgbm"]["rul"] = int(catboost_rul.predict(input_features)[0])

        return results

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
