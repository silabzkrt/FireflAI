# Wildfire Risk Prediction Model (XGBoost)

This repository contains the Machine Learning model designed to predict wildfire risk probabilities. The model processes real-time and historical meteorological data, topography, vegetation indices, and active fire data to generate a wildfire risk score ranging from 0% to 100%.

This model is used in an early fire detection system. A link to the main project repository will be added once the project is finalized.

---

## Model Summary

- Algorithm: XGBoost Classifier (XGBClassifier)
- Output: Wildfire risk probability score (%0 - %100)
- Model File: production_fire_model_xgboost.joblib
- Objective: Calculate the wildfire risk score for a specific coordinate based on input features.

---

## Dataset and Training

- Dataset Size: 1,800 records of physically accurate generated environmental data.
- Geographic Scope: Turkey land boundaries (Mediterranean, Aegean, Black Sea, and Inland micro-climates).
- Integrated Data Sources: Open-Meteo API, NASA FIRMS (VIIRS), and DEM elevation data.

---

## Input Features (27 Variables)

The model requires 27 specific parameters to compute the risk score:

1. Meteorology (Live and Past Accumulations)
- Temperature: Live 2m air temperature (°C)
- RH: Live relative humidity (%)
- Ws: Wind speed at 10m (km/h)
- Wind_Direction: Wind direction in degrees (0°–360°)
- Rain: Live precipitation amount (mm)
- Rain_3D_Sum: Cumulative rainfall over the last 3 days (mm)
- Rain_7D_Sum: Cumulative rainfall over the last 7 days (mm)
- Temp_3D_Max: Maximum temperature recorded in the last 3 days (°C)
- RH_3D_Mean: Average relative humidity over the last 3 days (%)

2. Derived Risk Indices
- Dryness_Index: Dryness ratio derived from temperature and humidity (Temp / (RH + 1e-5))
- VPD: Vapor Pressure Deficit (kPa)
- Resin_Ignition_Potential: Resin potential calculated using vegetation type, NDVI, and dryness

3. Soil and Hydrology
- Surface_Temp: Land surface temperature (°C)
- Soil_Temp: Soil temperature at 0–10cm depth (°C)
- Soil_Moisture: Soil moisture content at 0–10cm depth (m³/m³)
- Dew_Point: Dew point temperature (°C)
- Pressure: Surface pressure (hPa)
- Evapotranspiration: FAO evapotranspiration rate (mm)

4. Time Variables
- is_day: Day (1) / Night (0) indicator
- month_sin, month_cos: Sine and cosine cyclical transformations of the month
- hour_sin, hour_cos: Sine and cosine cyclical transformations of the hour

5. Vegetation and Land Cover
- NDVI: Normalized Difference Vegetation Index
- Fuel_Type_Conifer: Coniferous forest density ratio (0.0 – 1.0)

6. Active Fire Alignment and Proximity
- Nearest_Fire_Dist_KM: Distance to the nearest active NASA FIRMS fire point (km)
- Wind_Fire_Vector_Alignment: Angle difference between wind direction and nearest active fire vector (°)

---

## Risk Thresholds

- 0% - 39%: Low Risk
- 40% - 60%: Medium Risk
- 61% - 85%: High Risk
- 86% - 100%: Critical Risk (Rendered and highlighted directly on the map)
