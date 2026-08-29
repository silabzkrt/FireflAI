from datetime import datetime, timedelta
import json
import math
import os
import time
import urllib.error
import urllib.request
import joblib
import numpy as np
import pandas as pd

ELEVATION_API_URL = "https://api.open-elevation.com/api/v1/lookup?locations={lat},{lon}|{lat_offset},{lon}"
FIRMS_API_KEY = "e51623bd04cdb9f80855b5b27eb3be30"

FIRMS_NRT_URL = (
    "https://firms.modaps.eosdis.nasa.gov/api/area/csv/{api_key}/VIIRS_SNPP_NRT/"
    "{bbox_lon_min:.2f},{bbox_lat_min:.2f},{bbox_lon_max:.2f},{bbox_lat_max:.2f}/1"
)
FIRMS_ARCHIVE_VIIRS_URL = (
    "https://firms.modaps.eosdis.nasa.gov/api/area/csv/{api_key}/VIIRS_SNPP_SP/"
    "{bbox_lon_min:.2f},{bbox_lat_min:.2f},{bbox_lon_max:.2f},{bbox_lat_max:.2f}/1/{target_date}"
)
FIRMS_ARCHIVE_MODIS_URL = (
    "https://firms.modaps.eosdis.nasa.gov/api/area/csv/{api_key}/MODIS_SP/"
    "{bbox_lon_min:.2f},{bbox_lat_min:.2f},{bbox_lon_max:.2f},{bbox_lat_max:.2f}/1/{target_date}"
)

AIR_QUALITY_API_URL = "https://air-quality-api.open-meteo.com/v1/air-quality?latitude={lat}&longitude={lon}&current=pm2_5"
WEATHER_FORECAST_URL = (
    "https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
    "&current=temperature_2m,relative_humidity_2m,rain,wind_speed_10m,wind_direction_10m,is_day,"
    "surface_temperature,soil_temperature_0_to_10cm,soil_moisture_0_to_10cm,dew_point_2m,surface_pressure,et0_fao_evapotranspiration"
    "&hourly=rain,temperature_2m,relative_humidity_2m&past_days=7&timezone=auto"
)
WEATHER_ARCHIVE_URL = (
    "https://archive-api.open-meteo.com/v1/archive?latitude={lat}&longitude={lon}"
    "&start_date={start_date}&end_date={target_date}"
    "&hourly=temperature_2m,relative_humidity_2m,rain,wind_speed_10m,wind_direction_10m,"
    "surface_temperature,soil_temperature_0_to_10cm,soil_moisture_0_to_10cm,dew_point_2m,"
    "surface_pressure,et0_fao_evapotranspiration&timezone=auto"
)

script_dir = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(script_dir, "production_fire_model_xgboost.joblib")

try:
    model = joblib.load(model_path)
except Exception as e:
    raise RuntimeError(f"Model could not be loaded from '{model_path}': {e}")

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

def fetch_with_retry(url, retries=2, delay=0.5):
    """Executes HTTP requests with retries."""
    for attempt in range(retries):
        try:
            req = urllib.request.Request(
                url, headers={"User-Agent": "Mozilla/5.0"}
            )
            with urllib.request.urlopen(req, timeout=8) as response:
                return response.read().decode("utf-8")
        except Exception:
            if attempt < retries - 1:
                time.sleep(delay)
                continue
    return ""


def calculate_vpd(temp, rh):
    """Calculates Vapor Pressure Deficit (VPD) in kPa."""
    svp = 0.61078 * np.exp((17.27 * temp) / (temp + 237.3))
    avp = svp * (rh / 100.0)
    return round(float(svp - avp), 4)


def get_real_slope_from_dem(lat, lon):
    """Calculates terrain slope using Open-Elevation DEM API."""
    lat_offset = lat + 0.0009
    url = ELEVATION_API_URL.format(lat=lat, lon=lon, lat_offset=lat_offset)
    try:
        raw_data = fetch_with_retry(url, retries=1, delay=0.5)
        data = json.loads(raw_data)
        results = data["results"]
        ele1 = results[0]["elevation"]
        ele2 = results[1]["elevation"]
        slope_rad = math.atan(abs(ele2 - ele1) / 100.0)
        return round(math.degrees(slope_rad), 2)
    except Exception:
        return 0.0


def get_biomass_and_fuel_data(lat, lon):
    """Determines NDVI and conifer ratio based on geographic region."""
    if lat == 0.0 and lon == 0.0:
        return 0.0, 0.0

    is_mediterranean = (
        (30.0 <= lat <= 45.0 and -10.0 <= lon <= 40.0)
        or (32.0 <= lat <= 42.0 and -125.0 <= lon <= -115.0)
        or (-35.0 <= lat <= -30.0 and -73.0 <= lon <= -69.0)
    )
    return (0.60, 0.85) if is_mediterranean else (0.40, 0.15)


def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculates great-circle distance between two coordinates in KM."""
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2) ** 2
    )
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def calculate_wind_fire_alignment(
    target_lat, target_lon, fire_lat, fire_lon, wind_dir
):
    """Calculates angular alignment between wind vector and fire vector."""
    dlon = math.radians(target_lon - fire_lon)
    lat1, lat2 = math.radians(fire_lat), math.radians(target_lat)
    x = math.sin(dlon) * math.cos(lat2)
    y = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(
        lat2
    ) * math.cos(dlon)
    bearing = (math.degrees(math.atan2(x, y)) + 360) % 360
    wind_push_dir = (wind_dir + 180) % 360
    angle_diff = abs(wind_push_dir - bearing)
    if angle_diff > 180:
        angle_diff = 360 - angle_diff
    return round(angle_diff, 1)

def fetch_auto_active_fire_data(lat, lon, wind_dir, target_date=None):
    """Fetches active fire distance using NASA FIRMS Area API.

    - Live (no target_date): Uses VIIRS_SNPP_NRT
    - Historical (target_date provided): Queries VIIRS_SNPP_SP and MODIS_SP
    """
    min_dist = 100.0
    best_alignment = 180.0

    bbox_lat_min, bbox_lat_max = lat - 0.5, lat + 0.5
    bbox_lon_min, bbox_lon_max = lon - 0.5, lon + 0.5

    urls_to_try = []

    if target_date:
        urls_to_try.append(
            FIRMS_ARCHIVE_VIIRS_URL.format(
                api_key=FIRMS_API_KEY,
                bbox_lon_min=bbox_lon_min,
                bbox_lat_min=bbox_lat_min,
                bbox_lon_max=bbox_lon_max,
                bbox_lat_max=bbox_lat_max,
                target_date=target_date,
            )
        )
        urls_to_try.append(
            FIRMS_ARCHIVE_MODIS_URL.format(
                api_key=FIRMS_API_KEY,
                bbox_lon_min=bbox_lon_min,
                bbox_lat_min=bbox_lat_min,
                bbox_lon_max=bbox_lon_max,
                bbox_lat_max=bbox_lat_max,
                target_date=target_date,
            )
        )
    else:
        urls_to_try.append(
            FIRMS_NRT_URL.format(
                api_key=FIRMS_API_KEY,
                bbox_lon_min=bbox_lon_min,
                bbox_lat_min=bbox_lat_min,
                bbox_lon_max=bbox_lon_max,
                bbox_lat_max=bbox_lat_max,
            )
        )

    for url in urls_to_try:
        try:
            raw_csv = fetch_with_retry(url, retries=1, delay=0.5)
            lines = raw_csv.strip().splitlines()

            if len(lines) > 1 and lines[0].startswith("latitude"):
                headers = [h.strip() for h in lines[0].split(",")]
                lat_idx = headers.index("latitude")
                lon_idx = headers.index("longitude")

                for line in lines[1:]:
                    parts = line.split(",")
                    f_lat = float(parts[lat_idx])
                    f_lon = float(parts[lon_idx])

                    dist = haversine_distance(lat, lon, f_lat, f_lon)
                    if dist < min_dist:
                        min_dist = dist
                        best_alignment = calculate_wind_fire_alignment(
                            lat, lon, f_lat, f_lon, wind_dir
                        )

                if min_dist < 100.0:
                    break
        except Exception:
            continue

    if min_dist == 100.0 and not target_date:
        try:
            aq_url = AIR_QUALITY_API_URL.format(lat=lat, lon=lon)
            raw_aq = fetch_with_retry(aq_url, retries=1, delay=0.5)
            aq_data = json.loads(raw_aq)
            pm25 = float(aq_data.get("current", {}).get("pm2_5") or 0.0)

            if pm25 > 50.0:
                min_dist = 0.5
                best_alignment = 0.0
        except Exception:
            pass

    return round(min_dist, 2), best_alignment

def analyze_production_fire_risk(location_name, lat, lon, target_date=None):
    real_slope = get_real_slope_from_dem(lat, lon)
    ndvi, fuel_conifer = get_biomass_and_fuel_data(lat, lon)

    if target_date:
        dt_target = datetime.strptime(target_date, "%Y-%m-%d")
        start_date = (dt_target - timedelta(days=7)).strftime("%Y-%m-%d")
        api_url = WEATHER_ARCHIVE_URL.format(
            lat=lat, lon=lon, start_date=start_date, target_date=target_date
        )

        raw_weather = fetch_with_retry(api_url, retries=2, delay=1.0)
        data = json.loads(raw_weather) if raw_weather else {}
        hourly = data.get("hourly", {})

        idx = -11 if len(hourly.get("temperature_2m", [])) >= 12 else -1

        live_temp = float(hourly.get("temperature_2m", [20.0])[idx] or 20.0)
        live_rh = float(
            hourly.get("relative_humidity_2m", [50.0])[idx] or 50.0
        )
        live_ws = float(hourly.get("wind_speed_10m", [0.0])[idx] or 0.0)
        live_wdir = float(hourly.get("wind_direction_10m", [0.0])[idx] or 0.0)
        live_rain = float(hourly.get("rain", [0.0])[idx] or 0.0)
        is_day = 1

        month_int = dt_target.month
        hour_int = 13

        surf_temp = float(
            hourly.get("surface_temperature", [live_temp])[idx] or live_temp
        )
        soil_temp = float(
            hourly.get("soil_temperature_0_to_10cm", [live_temp])[idx]
            or live_temp
        )
        soil_moist = float(
            hourly.get("soil_moisture_0_to_10cm", [0.1])[idx] or 0.1
        )
        dew_point = float(hourly.get("dew_point_2m", [10.0])[idx] or 10.0)
        pressure = float(
            hourly.get("surface_pressure", [1013.25])[idx] or 1013.25
        )
        evap = float(
            hourly.get("et0_fao_evapotranspiration", [0.0])[idx] or 0.0
        )

    else:
        api_url = WEATHER_FORECAST_URL.format(lat=lat, lon=lon)
        raw_weather = fetch_with_retry(api_url, retries=2, delay=1.0)
        data = json.loads(raw_weather) if raw_weather else {}
        current = data.get("current", {})
        hourly = data.get("hourly", {})

        live_temp = float(current.get("temperature_2m") or 20.0)
        live_rh = float(current.get("relative_humidity_2m") or 50.0)
        live_ws = float(current.get("wind_speed_10m") or 0.0)
        live_wdir = float(current.get("wind_direction_10m") or 0.0)
        live_rain = float(current.get("rain") or 0.0)
        is_day = int(current.get("is_day", 1))

        current_time_str = current.get("time", "")
        if current_time_str:
            dt_obj = datetime.fromisoformat(current_time_str)
            month_int = dt_obj.month
            hour_int = dt_obj.hour
        else:
            now = datetime.now()
            month_int = now.month
            hour_int = now.hour

        surf_temp = float(current.get("surface_temperature") or live_temp)
        soil_temp = float(
            current.get("soil_temperature_0_to_10cm") or live_temp
        )
        soil_moist_raw = current.get("soil_moisture_0_to_10cm")
        soil_moist = (
            float(soil_moist_raw) if soil_moist_raw is not None else 0.0
        )

        dew_point = float(current.get("dew_point_2m") or 10.0)
        pressure = float(current.get("surface_pressure") or 1013.25)
        evap = float(current.get("et0_fao_evapotranspiration") or 0.0)

    if soil_moist == 0.0 or (lat == 0.0 and lon == 0.0):
        ndvi = 0.0
        fuel_conifer = 0.0

    is_desert_region = (
        (12.0 <= lat <= 35.0 and -18.0 <= lon <= 60.0)
        or (30.0 <= lat <= 42.0 and -120.0 <= lon <= -105.0)
        or (-30.0 <= lat <= -15.0 and -75.0 <= lon <= -60.0)
    )
    if is_desert_region:
        ndvi = 0.01
        fuel_conifer = 0.0

    past_rains = [
        float(r) if r is not None else 0.0 for r in hourly.get("rain", [])
    ]
    past_temps = [
        float(t) if t is not None else live_temp
        for t in hourly.get("temperature_2m", [])
    ]
    past_rhs = [
        float(h) if h is not None else live_rh
        for h in hourly.get("relative_humidity_2m", [])
    ]

    rain_3d_sum = round(sum(past_rains[-72:]), 2) if past_rains else 0.0
    rain_7d_sum = round(sum(past_rains[-168:]), 2) if past_rains else 0.0
    temp_3d_max = round(max(past_temps[-72:]), 2) if past_temps else live_temp
    rh_3d_mean = (
        round(float(np.mean(past_rhs[-72:])), 2) if past_rhs else live_rh
    )

    live_dryness = float(live_temp / (live_rh + 1e-5))
    vpd = calculate_vpd(live_temp, live_rh)
    resin_potential = round(
        (live_temp / (live_rh + 1.0)) * fuel_conifer * ndvi, 4
    )

    month_sin = round(float(np.sin(2 * np.pi * month_int / 12)), 4)
    month_cos = round(float(np.cos(2 * np.pi * month_int / 12)), 4)
    hour_sin = round(float(np.sin(2 * np.pi * hour_int / 24)), 4)
    hour_cos = round(float(np.cos(2 * np.pi * hour_int / 24)), 4)

    nearest_fire_dist, vector_align = fetch_auto_active_fire_data(
        lat, lon, live_wdir, target_date=target_date
    )

    input_dict = {
        "Temperature": [float(live_temp)],
        "RH": [float(live_rh)],
        "Ws": [float(live_ws)],
        "Wind_Direction": [float(live_wdir)],
        "Rain": [float(live_rain)],
        "Rain_3D_Sum": [float(rain_3d_sum)],
        "Rain_7D_Sum": [float(rain_7d_sum)],
        "Temp_3D_Max": [float(temp_3d_max)],
        "RH_3D_Mean": [float(rh_3d_mean)],
        "Dryness_Index": [float(live_dryness)],
        "VPD": [float(vpd)],
        "Surface_Temp": [float(surf_temp)],
        "Soil_Temp": [float(soil_temp)],
        "Soil_Moisture": [float(soil_moist)],
        "Dew_Point": [float(dew_point)],
        "Pressure": [float(pressure)],
        "Evapotranspiration": [float(evap)],
        "is_day": [int(is_day)],
        "month_sin": [float(month_sin)],
        "month_cos": [float(month_cos)],
        "hour_sin": [float(hour_sin)],
        "hour_cos": [float(hour_cos)],
        "NDVI": [float(ndvi)],
        "Fuel_Type_Conifer": [float(fuel_conifer)],
        "Resin_Ignition_Potential": [float(resin_potential)],
        "Nearest_Fire_Dist_KM": [float(nearest_fire_dist)],
        "Wind_Fire_Vector_Alignment": [float(vector_align)],
    }

    input_data = pd.DataFrame(input_dict)[feature_columns]

    prob = model.predict_proba(input_data)[:, 1][0]
    boosted_prob = np.clip(prob * 1.25, 0.0, 1.0) 
    final_score = round(float(boosted_prob * 100), 2)

    if final_score < 30.0:
        status = "LOW RISK"
    elif final_score < 65.0:
        status = "MEDIUM RISK"
    else:
        status = "HIGH RISK"

    day_status = "DAYTIME" if is_day == 1 else "NIGHTTIME"

    return {
        "location_name": location_name,
        "latitude": lat,
        "longitude": lon,
        "day_status": day_status,
        "month": month_int,
        "hour": hour_int,
        "real_slope": real_slope,
        "ndvi": ndvi,
        "fuel_conifer": fuel_conifer,
        "resin_potential": resin_potential,
        "temperature": live_temp,
        "rh": live_rh,
        "wind_speed": live_ws,
        "wind_direction": live_wdir,
        "nearest_fire_dist": nearest_fire_dist,
        "vector_alignment": vector_align,
        "rain_3d_sum": rain_3d_sum,
        "rain_7d_sum": rain_7d_sum,
        "temp_3d_max": temp_3d_max,
        "rh_3d_mean": rh_3d_mean,
        "soil_moisture": soil_moist,
        "vpd": vpd,
        "evapotranspiration": evap,
        "risk_score": final_score,
        "status": status,
    }

def print_fire_risk_report(result):
    if not result:
        return
    print(
        f"================ PRODUCTION RISK ANALYSIS:"
        f" {result['location_name'].upper()} ================"
    )
    print(
        f"Coordinates        -> Lat: {result['latitude']}, Lon:"
        f" {result['longitude']}"
    )
    print(
        f"Time / Status      -> {result['day_status']} | Month:"
        f" {result['month']} | Hour: {result['hour']}:00"
    )
    print(f"Topography (DEM)   -> Real Slope: {result['real_slope']}°")
    print(
        f"Vegetation/Biomass -> NDVI: {result['ndvi']} | Conifer Ratio:"
        f" {result['fuel_conifer'] * 100:.0f}% | Resin Potential:"
        f" {result['resin_potential']}"
    )
    print(
        f"Live Meteorology   -> Temp: {result['temperature']}°C | RH:"
        f" {result['rh']}% | Wind: {result['wind_speed']} km/h (Dir:"
        f" {result['wind_direction']}°)"
    )
    print(
        f"Active Fire Spread -> Nearest Fire: {result['nearest_fire_dist']} km |"
        f" Vector Align: {result['vector_alignment']}°"
    )
    print(
        f"Historical Accum.  -> 3-Day Rain: {result['rain_3d_sum']} mm | 7-Day"
        f" Rain: {result['rain_7d_sum']} mm"
    )
    print(
        f"                      3-Day Max Temp:"
        f" {result['temp_3d_max']}°C | 3-Day Mean RH: {result['rh_3d_mean']}%"
    )
    print(
        f"Hydrology / Soil   -> Soil Moisture: {result['soil_moisture']} m³/m³"
        f" | VPD: {result['vpd']} kPa | Evapotranspiration:"
        f" {result['evapotranspiration']} mm"
    )
    print(
        "--------------------------------------------------------------------------------"
    )
    print(
        f"NET RISK SCORE     -> Score: {result['risk_score']}% | STATUS:"
        f" {result['status']}"
    )
    print(
        "================================================================================\n"
    )


if __name__ == "__main__":
    test_res = analyze_production_fire_risk(
        "Seferihisar Test", 38.193663, 26.853315
    )
    print_fire_risk_report(test_res)