import os
import numpy as np
import pandas as pd

script_dir = os.path.dirname(os.path.abspath(__file__))
output_path = os.path.join(script_dir, "fire_dataset.csv")

def calculate_vpd(temp, rh):
    svp = 0.61078 * np.exp((17.27 * temp) / (temp + 237.3))
    avp = svp * (rh / 100.0)
    return np.round(svp - avp, 4)

def generate_fire_dataset(num_samples=2400):
    np.random.seed(42)
    quarter_count = num_samples // 4

    high_temp = np.random.uniform(33.0, 45.0, quarter_count)
    high_rh = np.random.uniform(8.0, 25.0, quarter_count)
    high_ws = np.random.uniform(15.0, 45.0, quarter_count)
    high_wdir = np.random.uniform(0.0, 360.0, quarter_count)
    high_rain = np.zeros(quarter_count)
    high_rain_3d = np.random.exponential(0.1, quarter_count)
    high_rain_7d = np.random.exponential(0.2, quarter_count)
    high_temp_3d_max = high_temp + np.random.uniform(0.0, 3.0, quarter_count)
    high_rh_3d_mean = high_rh + np.random.uniform(0.0, 5.0, quarter_count)
    high_surf_temp = high_temp + np.random.uniform(5.0, 15.0, quarter_count)
    high_soil_temp = high_temp + np.random.uniform(3.0, 10.0, quarter_count)
    high_soil_moist = np.random.uniform(0.01, 0.08, quarter_count)
    high_dew_point = high_temp - np.random.uniform(20.0, 30.0, quarter_count)
    high_pressure = np.random.uniform(995.0, 1010.0, quarter_count)
    high_evap = np.random.uniform(6.0, 12.0, quarter_count)
    high_is_day = np.ones(quarter_count, dtype=int)
    high_month = np.random.choice([7, 8], size=quarter_count)
    high_hour = np.random.choice(range(12, 18), size=quarter_count)

    high_ndvi = np.random.uniform(0.35, 0.85, quarter_count)
    high_conifer = np.random.uniform(0.30, 0.95, quarter_count)

    high_fire_dist = np.random.uniform(0.5, 10.0, quarter_count)
    high_vector_align = np.random.uniform(0.0, 25.0, quarter_count)
    high_is_fire = np.ones(quarter_count, dtype=int)

    med_temp = np.random.uniform(28.0, 34.0, quarter_count)
    med_rh = np.random.uniform(30.0, 50.0, quarter_count)
    med_ws = np.random.uniform(10.0, 22.0, quarter_count)
    med_wdir = np.random.uniform(0.0, 360.0, quarter_count)
    med_rain = np.random.exponential(0.5, quarter_count)
    med_rain_3d = np.random.exponential(1.5, quarter_count)
    med_rain_7d = np.random.exponential(3.0, quarter_count)
    med_temp_3d_max = med_temp + np.random.uniform(-1.0, 2.0, quarter_count)
    med_rh_3d_mean = med_rh + np.random.uniform(-2.0, 8.0, quarter_count)
    med_surf_temp = med_temp + np.random.uniform(1.0, 5.0, quarter_count)
    med_soil_temp = med_temp + np.random.uniform(0.0, 4.0, quarter_count)
    med_soil_moist = np.random.uniform(0.09, 0.18, quarter_count)
    med_dew_point = med_temp - np.random.uniform(10.0, 18.0, quarter_count)
    med_pressure = np.random.uniform(1008.0, 1018.0, quarter_count)
    med_evap = np.random.uniform(3.0, 6.0, quarter_count)
    med_is_day = np.random.choice([1, 0], size=quarter_count, p=[0.7, 0.3])
    med_month = np.random.choice([6, 7, 8, 9], size=quarter_count)
    med_hour = np.random.choice(range(9, 20), size=quarter_count)

    med_ndvi = np.random.uniform(0.20, 0.50, quarter_count)
    med_conifer = np.random.uniform(0.10, 0.50, quarter_count)

    med_fire_dist = np.random.uniform(10.0, 35.0, quarter_count)
    med_vector_align = np.random.uniform(20.0, 70.0, quarter_count)
    med_is_fire = np.random.choice([1, 0], size=quarter_count, p=[0.30, 0.70])

    low_temp = np.random.uniform(5.0, 25.0, quarter_count)
    low_rh = np.random.uniform(45.0, 95.0, quarter_count)
    low_ws = np.random.uniform(1.0, 15.0, quarter_count)
    low_wdir = np.random.uniform(0.0, 360.0, quarter_count)
    low_rain = np.random.exponential(2.0, quarter_count)
    low_rain_3d = np.random.exponential(6.0, quarter_count)
    low_rain_7d = np.random.exponential(15.0, quarter_count)
    low_temp_3d_max = low_temp + np.random.uniform(-3.0, 1.0, quarter_count)
    low_rh_3d_mean = low_rh + np.random.uniform(-2.0, 10.0, quarter_count)
    low_surf_temp = low_temp + np.random.uniform(-2.0, 2.0, quarter_count)
    low_soil_temp = low_temp + np.random.uniform(-2.0, 2.0, quarter_count)
    low_soil_moist = np.random.uniform(0.18, 0.45, quarter_count)
    low_dew_point = low_temp - np.random.uniform(1.0, 8.0, quarter_count)
    low_pressure = np.random.uniform(1012.0, 1025.0, quarter_count)
    low_evap = np.random.uniform(0.0, 3.0, quarter_count)
    low_is_day = np.random.choice([1, 0], size=quarter_count, p=[0.3, 0.7])
    low_month = np.random.choice([1, 2, 3, 4, 5, 10, 11, 12], size=quarter_count)
    low_hour = np.random.choice(range(0, 24), size=quarter_count)

    low_ndvi = np.random.uniform(0.10, 0.60, quarter_count)
    low_conifer = np.random.uniform(0.0, 0.30, quarter_count)

    low_fire_dist = np.random.uniform(50.0, 150.0, quarter_count)
    low_vector_align = np.random.uniform(80.0, 180.0, quarter_count)
    low_is_fire = np.zeros(quarter_count, dtype=int)

    special_temp = np.random.uniform(25.0, 52.0, quarter_count)
    special_rh = np.random.uniform(5.0, 90.0, quarter_count)
    special_ws = np.random.uniform(2.0, 30.0, quarter_count)
    special_wdir = np.random.uniform(0.0, 360.0, quarter_count)
    special_rain = np.zeros(quarter_count)
    special_rain_3d = np.zeros(quarter_count)
    special_rain_7d = np.zeros(quarter_count)
    special_temp_3d_max = special_temp + np.random.uniform(0.0, 3.0, quarter_count)
    special_rh_3d_mean = special_rh
    special_surf_temp = special_temp + np.random.uniform(0.0, 15.0, quarter_count)
    special_soil_temp = special_temp
    special_soil_moist = np.random.choice([0.0, 0.01], size=quarter_count)
    special_dew_point = special_temp - np.random.uniform(10.0, 35.0, quarter_count)
    special_pressure = np.random.uniform(1005.0, 1020.0, quarter_count)
    special_evap = np.random.uniform(0.0, 15.0, quarter_count)
    special_is_day = np.random.choice([1, 0], size=quarter_count)
    special_month = np.random.choice(range(1, 13), size=quarter_count)
    special_hour = np.random.choice(range(0, 24), size=quarter_count)

    special_ndvi = np.random.uniform(0.0, 0.04, quarter_count)
    special_conifer = np.zeros(quarter_count)

    special_fire_dist = np.full(quarter_count, 100.0)
    special_vector_align = np.full(quarter_count, 180.0)
    special_is_fire = np.zeros(quarter_count, dtype=int)

    temp = np.concatenate([high_temp, med_temp, low_temp, special_temp])
    rh = np.concatenate([high_rh, med_rh, low_rh, special_rh])
    ws = np.concatenate([high_ws, med_ws, low_ws, special_ws])
    wdir = np.concatenate([high_wdir, med_wdir, low_wdir, special_wdir])
    rain = np.concatenate([high_rain, med_rain, low_rain, special_rain])
    rain_3d = np.concatenate([high_rain_3d, med_rain_3d, low_rain_3d, special_rain_3d])
    rain_7d = np.concatenate([high_rain_7d, med_rain_7d, low_rain_7d, special_rain_7d])
    temp_3d_max = np.concatenate([high_temp_3d_max, med_temp_3d_max, low_temp_3d_max, special_temp_3d_max])
    rh_3d_mean = np.concatenate([high_rh_3d_mean, med_rh_3d_mean, low_rh_3d_mean, special_rh_3d_mean])
    surf_temp = np.concatenate([high_surf_temp, med_surf_temp, low_surf_temp, special_surf_temp])
    soil_temp = np.concatenate([high_soil_temp, med_soil_temp, low_soil_temp, special_soil_temp])
    soil_moist = np.concatenate([high_soil_moist, med_soil_moist, low_soil_moist, special_soil_moist])
    dew_point = np.concatenate([high_dew_point, med_dew_point, low_dew_point, special_dew_point])
    pressure = np.concatenate([high_pressure, med_pressure, low_pressure, special_pressure])
    evap = np.concatenate([high_evap, med_evap, low_evap, special_evap])
    is_day = np.concatenate([high_is_day, med_is_day, low_is_day, special_is_day])
    month = np.concatenate([high_month, med_month, low_month, special_month])
    hour = np.concatenate([high_hour, med_hour, low_hour, special_hour])

    ndvi = np.concatenate([high_ndvi, med_ndvi, low_ndvi, special_ndvi])
    fuel_conifer = np.concatenate([high_conifer, med_conifer, low_conifer, special_conifer])

    fire_dist = np.concatenate([high_fire_dist, med_fire_dist, low_fire_dist, special_fire_dist])
    vector_align = np.concatenate([high_vector_align, med_vector_align, low_vector_align, special_vector_align])
    is_fire = np.concatenate([high_is_fire, med_is_fire, low_is_fire, special_is_fire])

    dryness = np.round(temp / (rh + 1e-5), 3)
    vpd = calculate_vpd(temp, rh)
    resin_potential = np.round((temp / (rh + 1.0)) * fuel_conifer * ndvi, 4)

    month_sin = np.round(np.sin(2 * np.pi * month / 12), 4)
    month_cos = np.round(np.cos(2 * np.pi * month / 12), 4)
    hour_sin = np.round(np.sin(2 * np.pi * hour / 24), 4)
    hour_cos = np.round(np.cos(2 * np.pi * hour / 24), 4)

    df = pd.DataFrame({
        "Temperature": np.round(temp, 2),
        "RH": np.round(rh, 2),
        "Ws": np.round(ws, 2),
        "Wind_Direction": np.round(wdir, 1),
        "Rain": np.round(rain, 2),
        "Rain_3D_Sum": np.round(rain_3d, 2),
        "Rain_7D_Sum": np.round(rain_7d, 2),
        "Temp_3D_Max": np.round(temp_3d_max, 2),
        "RH_3D_Mean": np.round(rh_3d_mean, 2),
        "Dryness_Index": dryness,
        "VPD": vpd,
        "Surface_Temp": np.round(surf_temp, 2),
        "Soil_Temp": np.round(soil_temp, 2),
        "Soil_Moisture": np.round(soil_moist, 3),
        "Dew_Point": np.round(dew_point, 2),
        "Pressure": np.round(pressure, 1),
        "Evapotranspiration": np.round(evap, 2),
        "is_day": is_day,
        "month_sin": month_sin,
        "month_cos": month_cos,
        "hour_sin": hour_sin,
        "hour_cos": hour_cos,
        "NDVI": np.round(ndvi, 3),
        "Fuel_Type_Conifer": np.round(fuel_conifer, 3),
        "Resin_Ignition_Potential": resin_potential,
        "Nearest_Fire_Dist_KM": np.round(fire_dist, 2),
        "Wind_Fire_Vector_Alignment": np.round(vector_align, 1),
        "is_fire": is_fire
    })

    df = df.sample(frac=1.0, random_state=42).reset_index(drop=True)
    df.to_csv(output_path, index=False)
    print(f"PHYSICS-CALIBRATED DATASET CREATED ({len(df)} Rows): {output_path}")

generate_fire_dataset()