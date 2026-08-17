import os
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier

script_dir = os.path.dirname(os.path.abspath(__file__))
dataset_path = os.path.join(script_dir, "fire_dataset.csv")

print("Loading Dataset...")
df = pd.read_csv(dataset_path)

if "NDVI" not in df.columns:
    df["NDVI"] = 0.5
if "Fuel_Type_Conifer" not in df.columns:
    df["Fuel_Type_Conifer"] = 0.0

if "Nearest_Fire_Dist_KM" not in df.columns:
    df["Nearest_Fire_Dist_KM"] = 100.0
if "Wind_Fire_Vector_Alignment" not in df.columns:
    df["Wind_Fire_Vector_Alignment"] = 180.0

df["Resin_Ignition_Potential"] = (
    (df["Temperature"] / (df["RH"] + 1.0)) * df["Fuel_Type_Conifer"] * df["NDVI"]
)

feature_columns = [
    "Temperature",
    "RH",
    "Ws",
    "Wind_Direction",
    "Rain",
    "Rain_3D_Sum",
    "Rain_7D_Sum",
    "Temp_3D_Max",
    "RH_3D_Mean",
    "Dryness_Index",
    "VPD",
    "Surface_Temp",
    "Soil_Temp",
    "Soil_Moisture",
    "Dew_Point",
    "Pressure",
    "Evapotranspiration",
    "is_day",
    "month_sin",
    "month_cos",
    "hour_sin",
    "hour_cos",
    "NDVI",
    "Fuel_Type_Conifer",
    "Resin_Ignition_Potential",
    "Nearest_Fire_Dist_KM",
    "Wind_Fire_Vector_Alignment",
]

X = df[feature_columns]
y = df["is_fire"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

print(f"Training Calibrated Biomass + Fire-Spread Assisted XGBoost Model ({len(feature_columns)} Features)...")

model = XGBClassifier(
    n_estimators=100,
    learning_rate=0.03,
    max_depth=3,
    subsample=0.7,
    colsample_bytree=0.7,
    reg_alpha=1.0,
    reg_lambda=1.0,
    random_state=42,
    eval_metric="logloss",
)

model.fit(X_train, y_train)

model_save_path = os.path.join(script_dir, "production_fire_model_xgboost.joblib")
joblib.dump(model, model_save_path)

print(f"MODEL SUCCESSFULLY SAVED -> {model_save_path}")