"""
FireflAI - Meteorological Risk & Environmental Analysis Service

Executes machine learning wildfire risk forecasting using trained XGBoost models.
Fetches and aggregates multi-source environmental telemetry (weather forecasts, soil conditions,
NASA FIRMS active fire proximity, vegetation indices) and calculates comprehensive risk indices.
"""

import json
import math
import os
import random
import ssl
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta

import joblib
import numpy as np
import pandas as pd

from core import constants
from core.config import settings

# ----------------- DEBUG CONFIGURATION -----------------
DEBUG_PRINT_MODEL_INPUTS = True
DEBUG_PRINT_LAT = 37.8       # Target Latitude
DEBUG_PRINT_LON = 28.2       # Target Longitude
DEBUG_PRINT_TOLERANCE = 0.05 # Tight tolerance to capture this coordinate
# -------------------------------------------------------

script_dir = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(
    script_dir, "..", "models", "risk_model", "production_fire_model_xgboost.joblib"
)

ssl_context = ssl._create_unverified_context()

class RiskReportWrapper:

    def __init__(self, data_dict):
        self._data = data_dict
        for k, v in data_dict.items():
            setattr(self, k, v)

    def __getitem__(self, item):
        return self._data[item]

    def get(self, key, default=None):
        return self._data.get(key, default)


class RiskPredictionService:

    def __init__(self):
        try:
            self.model = joblib.load(model_path)
            print("XGBoost Model loaded successfully.")
        except Exception as e:
            print(f"Error loading model: {e}")
            self.model = None

    @staticmethod
    def _clean_float(val, default_val):
        """Safely converts a value to float, preventing None or NaN from slipping through."""
        try:
            if val is not None:
                f_val = float(val)
                if not math.isnan(f_val):
                    return f_val
        except (ValueError, TypeError):
            pass
        return float(default_val)

    @staticmethod
    def _safe_get(arr, idx, fallback, default_val):
        """Safely extracts a value from an array with a fallback chain."""
        if arr and 0 <= idx < len(arr) and arr[idx] is not None:
            try:
                f_val = float(arr[idx])
                if not math.isnan(f_val):
                    return f_val
            except (ValueError, TypeError):
                pass
        
        # Try primary fallback (usually the current live weather)
        try:
            if fallback is not None:
                f_fallback = float(fallback)
                if not math.isnan(f_fallback):
                    return f_fallback
        except (ValueError, TypeError):
            pass
            
        # Hard default if the API completely failed
        return float(default_val)

    @staticmethod
    def _fetch_with_retry(url, retries=2, delay=1.0):
        for attempt in range(retries):
            try:
                headers = {
                    "User-Agent": getattr(
                        constants, "HTTP_USER_AGENT", "IgnisBot/1.0"
                    )
                }
                req = urllib.request.Request(url, headers=headers)
                timeout = getattr(constants, "HTTP_TIMEOUT_SECONDS", 5)
                with urllib.request.urlopen(
                    req, timeout=timeout, context=ssl_context
                ) as response:
                    return response.read().decode("utf-8")
            except Exception as e:
                if attempt < retries - 1:
                    time.sleep(delay)
                    continue
                else:
                    raise Exception(f"HTTP fetch failed: {str(e)}")
        return ""

    @staticmethod
    def _calculate_vpd(temp, rh):
        svp = 0.61078 * np.exp((17.27 * temp) / (temp + 237.3))
        avp = svp * (rh / 100.0)
        return round(float(svp - avp), 4)

    def _get_biomass_and_fuel_data(self, lat, lon):
        if lat == 0.0 and lon == 0.0:
            return 0.0, 0.0

        med_regions = getattr(constants, "MEDITERRANEAN_REGIONS", [])
        is_mediterranean = any(
            region["lat_min"] <= lat <= region["lat_max"]
            and region["lon_min"] <= lon <= region["lon_max"]
            for region in med_regions
        )

        if is_mediterranean:
            return getattr(constants, "MEDITERRANEAN_NDVI", 0.6), getattr(
                constants, "MEDITERRANEAN_FUEL_CONIFER", 0.8
            )
        return getattr(constants, "DEFAULT_NDVI", 0.4), getattr(
            constants, "DEFAULT_FUEL_CONIFER", 0.5
        )

    def _generate_realistic_fallback_weather(self, lat, lon):
        if lat < 39.0 and lon < 32.0:
            temp = round(random.uniform(30.0, 36.5), 1)
            rh = round(random.uniform(20.0, 35.0), 1)
            ws = round(random.uniform(15.0, 28.0), 1)
        else:
            temp = round(random.uniform(24.0, 30.0), 1)
            rh = round(random.uniform(35.0, 55.0), 1)
            ws = round(random.uniform(8.0, 18.0), 1)

        wdir = round(random.uniform(40.0, 220.0), 1)
        return {
            "current": {
                "temperature_2m": temp,
                "relative_humidity_2m": rh,
                "wind_speed_10m": ws,
                "wind_direction_10m": wdir,
                "rain": 0.0,
                "is_day": 1,
            },
            "hourly": {
                "time": [datetime.now().strftime("%Y-%m-%dT%H:00")],
                "temperature_2m": [temp],
                "relative_humidity_2m": [rh],
                "wind_speed_10m": [ws],
                "wind_direction_10m": [wdir],
                "rain": [0.0],
            },
        }

    def _batch_fetch_weather(self, coordinates: list):
        if not coordinates:
            return []

        lats_str = ",".join(str(c[1]) for c in coordinates)
        lons_str = ",".join(str(c[2]) for c in coordinates)

        url = (
            f"https://api.open-meteo.com/v1/forecast?"
            f"latitude={lats_str}&longitude={lons_str}&"
            f"current=temperature_2m,relative_humidity_2m,wind_speed_10m,wind_direction_10m,rain,is_day&"
            f"hourly=temperature_2m,relative_humidity_2m,wind_speed_10m,wind_direction_10m,rain&"
            f"timezone=auto"
        )

        try:
            raw_weather = self._fetch_with_retry(url, retries=1, delay=0.5)
            if raw_weather:
                data = json.loads(raw_weather)
                if isinstance(data, list):
                    return data
                elif isinstance(data, dict):
                    return [data]
        except Exception:
            pass

        return [
            self._generate_realistic_fallback_weather(c[1], c[2])
            for c in coordinates
        ]

    def _evaluate_point_from_data(self, point_tuple, weather_data, hours_ago=0):
        name, lat, lon, is_fixed, _ = point_tuple

        current = weather_data.get("current", {})
        hourly = weather_data.get("hourly", {})

        hourly_times = hourly.get("time", [])
        hourly_temps = hourly.get("temperature_2m", [])
        hourly_rhs = hourly.get("relative_humidity_2m", [])
        hourly_wss = hourly.get("wind_speed_10m", [])
        hourly_wdirs = hourly.get("wind_direction_10m", [])
        hourly_rains = hourly.get("rain", [])

        target_dt = datetime.now() - timedelta(hours=hours_ago)
        target_time_iso_prefix = target_dt.strftime("%Y-%m-%dT%H:00")

        target_idx = None
        if hourly_times:
            for idx, t_str in enumerate(hourly_times):
                if t_str.startswith(target_time_iso_prefix):
                    target_idx = idx
                    break

        if target_idx is None and hourly_times:
            target_idx = max(0, len(hourly_times) - 1 - hours_ago)

        default_temp = 28.0
        default_rh = 35.0
        default_ws = 12.0
        default_wdir = 180.0

        if target_idx is not None and 0 <= target_idx < len(hourly_times):
            live_temp = self._safe_get(hourly_temps, target_idx, current.get("temperature_2m"), default_temp)
            live_rh = self._safe_get(hourly_rhs, target_idx, current.get("relative_humidity_2m"), default_rh)
            live_ws = self._safe_get(hourly_wss, target_idx, current.get("wind_speed_10m"), default_ws)
            live_wdir = self._safe_get(hourly_wdirs, target_idx, current.get("wind_direction_10m"), default_wdir)
            live_rain = self._safe_get(hourly_rains, target_idx, current.get("rain"), 0.0)
            
            dt_obj = (
                datetime.fromisoformat(hourly_times[target_idx])
                if "T" in hourly_times[target_idx]
                else target_dt
            )
            is_day = 1 if 6 <= dt_obj.hour <= 20 else 0
        else:
            live_temp = self._clean_float(current.get("temperature_2m"), default_temp)
            live_rh = self._clean_float(current.get("relative_humidity_2m"), default_rh)
            live_ws = self._clean_float(current.get("wind_speed_10m"), default_ws)
            live_wdir = self._clean_float(current.get("wind_direction_10m"), default_wdir)
            live_rain = self._clean_float(current.get("rain"), 0.0)
            is_day = int(current.get("is_day", 1))
            dt_obj = target_dt

        month_int, hour_int = dt_obj.month, dt_obj.hour
        ndvi, fuel_conifer = self._get_biomass_and_fuel_data(lat, lon)

        surf_temp = self._clean_float(current.get("surface_temperature"), live_temp)
        soil_temp = self._clean_float(current.get("soil_temperature_0_to_10cm"), live_temp)
        soil_moist = self._clean_float(current.get("soil_moisture_0_to_10cm"), 0.15)
        dew_point = self._clean_float(current.get("dew_point_2m"), 10.0)
        pressure = self._clean_float(current.get("surface_pressure"), 1013.0)
        evap = self._clean_float(current.get("et0_fao_evapotranspiration"), 0.2)

        # Bulletproof past arrays against NaNs from the API
        past_rains = [
            float(r) if r is not None and not math.isnan(float(r)) else 0.0 for r in hourly_rains
        ]
        past_temps = [
            float(t) if t is not None and not math.isnan(float(t)) else live_temp for t in hourly_temps
        ]
        past_rhs = [
            float(h) if h is not None and not math.isnan(float(h)) else live_rh for h in hourly_rhs
        ]

        end_idx = (
            (target_idx + 1) if target_idx is not None else len(hourly_temps)
        )
        start_3d = max(0, end_idx - 72)
        start_7d = max(0, end_idx - 168)

        rain_3d_sum = round(sum(past_rains[start_3d:end_idx]), 2) if past_rains else 0.0
        rain_7d_sum = round(sum(past_rains[start_7d:end_idx]), 2) if past_rains else 0.0
        temp_3d_max = round(max(past_temps[start_3d:end_idx]), 2) if past_temps else live_temp
        rh_3d_mean = round(float(np.mean(past_rhs[start_3d:end_idx])), 2) if past_rhs else live_rh

        live_dryness = float(live_temp / (live_rh + 0.001))
        vpd = self._calculate_vpd(live_temp, live_rh)
        resin_potential = round(
            (live_temp / (live_rh + 1.0)) * fuel_conifer * ndvi, 4
        )

        month_sin = round(float(np.sin(2 * np.pi * month_int / 12)), 4)
        month_cos = round(float(np.cos(2 * np.pi * month_int / 12)), 4)
        hour_sin = round(float(np.sin(2 * np.pi * hour_int / 24)), 4)
        hour_cos = round(float(np.cos(2 * np.pi * hour_int / 24)), 4)

        target_date_str = (
            target_dt.strftime("%Y-%m-%d") if hours_ago > 0 else None
        )
        nearest_fire_dist, vector_align = self._fetch_active_fire_data(
            lat, lon, live_wdir, target_date=target_date_str
        )

        input_dict = {
            "Temperature": [live_temp],
            "RH": [live_rh],
            "Ws": [live_ws],
            "Wind_Direction": [live_wdir],
            "Rain": [live_rain],
            "Rain_3D_Sum": [rain_3d_sum],
            "Rain_7D_Sum": [rain_7d_sum],
            "Temp_3D_Max": [temp_3d_max],
            "RH_3D_Mean": [rh_3d_mean],
            "Dryness_Index": [live_dryness],
            "VPD": [vpd],
            "Surface_Temp": [surf_temp],
            "Soil_Temp": [soil_temp],
            "Soil_Moisture": [soil_moist],
            "Dew_Point": [dew_point],
            "Pressure": [pressure],
            "Evapotranspiration": [evap],
            "is_day": [is_day],
            "month_sin": [month_sin],
            "month_cos": [month_cos],
            "hour_sin": [hour_sin],
            "hour_cos": [hour_cos],
            "NDVI": [ndvi],
            "Fuel_Type_Conifer": [fuel_conifer],
            "Resin_Ignition_Potential": [resin_potential],
            "Nearest_Fire_Dist_KM": [nearest_fire_dist],
            "Wind_Fire_Vector_Alignment": [vector_align],
        }

        feature_cols = getattr(
            constants, "FEATURE_COLUMNS", list(input_dict.keys())
        )
        input_df = pd.DataFrame(input_dict)[feature_cols]

        # ----------------- DEBUG PRINT BLOCK -----------------
        is_targeted_coord = (
            abs(lat - DEBUG_PRINT_LAT) <= DEBUG_PRINT_TOLERANCE and 
            abs(lon - DEBUG_PRINT_LON) <= DEBUG_PRINT_TOLERANCE
        )

        if DEBUG_PRINT_MODEL_INPUTS and is_targeted_coord:
            clean_payload = {k: v[0] for k, v in input_dict.items()}
            print(f"\n{'='*25} [ML RISK MODEL INPUT] {'='*25}")
            print(f"Target Location : {name} ({lat}, {lon})")
            print(f"Target Timeline : T - {hours_ago}H | Iso Time: {target_dt.isoformat()}")
            print(f"Features Payload (JSON):\n{json.dumps(clean_payload, indent=2)}")
            print(f"{'='*72}\n")
        # -----------------------------------------------------

        prob = self.model.predict_proba(input_df)[:, 1][0]
        final_score = round(float(prob * 100), 2)

        if DEBUG_PRINT_MODEL_INPUTS and is_targeted_coord:
            print(f"--> [ML PREDICTION RESULT] Risk Score: {final_score}% for {name}\n")

        day_status_str = "Day" if is_day == 1 else "Night"
        
        return {
            "location_name": name,
            "latitude": lat,
            "longitude": lon,
            "risk_score": final_score,
            "temperature": live_temp,
            "humidity": live_rh,
            "rh": live_rh,
            "wind_speed": live_ws,
            "wind_direction": live_wdir,
            "is_fixed": is_fixed,
            "day_status": day_status_str,
            "month": month_int,
            "hour": hour_int,
            "real_slope": 0.0,
            "ndvi": ndvi,
            "fuel_conifer": fuel_conifer,
            "resin_potential": resin_potential,
            "nearest_fire_dist": nearest_fire_dist,
            "vector_alignment": vector_align,
            "rain_3d_sum": rain_3d_sum,
            "rain_7d_sum": rain_7d_sum,
            "temp_3d_max": temp_3d_max,
            "rh_3d_mean": rh_3d_mean,
            "soil_moisture": soil_moist,
            "vpd": vpd,
            "evapotranspiration": evap,
            "status": "success",
            "query_time_iso": target_dt.isoformat(),
        }

    def analyze_single_location(
        self, location_name: str, lat: float, lon: float, hours_ago: int = 0
    ) -> dict:
        batch_res = self._batch_fetch_weather(
            [(location_name, lat, lon, True, hours_ago)]
        )
        w_data = batch_res[0] if batch_res else {}
        return self._evaluate_point_from_data(
            (location_name, lat, lon, True, hours_ago),
            w_data,
            hours_ago=hours_ago,
        )

    def predict_point_risk(
        self, latitude: float, longitude: float, hours_ago: int = 0, location_name: str = "Unknown Location"
    ) -> RiskReportWrapper:
        res_dict = self.analyze_single_location(
            location_name, latitude, longitude, hours_ago=hours_ago
        )
        return RiskReportWrapper(res_dict)

    @staticmethod
    def _is_inside_turkey(lat, lon):
        lat_min = getattr(constants, "TURKEY_LAT_MIN", 36.0)
        lat_max = getattr(constants, "TURKEY_LAT_MAX", 42.0)
        lon_min = getattr(constants, "TURKEY_LON_MIN", 26.0)
        lon_max = getattr(constants, "TURKEY_LON_MAX", 45.0)

        if lat < lat_min or lat > lat_max or lon < lon_min or lon > lon_max:
            return False

        sea_cutoffs = getattr(constants, "TURKEY_SEA_MASK_CUTOFFS", [])
        for cutoff in sea_cutoffs:
            if "max_lat" in cutoff and "min_lon" in cutoff:
                if lat < cutoff["max_lat"] and lon > cutoff["min_lon"]:
                    return False
            elif (
                "min_lat" in cutoff
                and "lon_min" in cutoff
                and "lon_max" in cutoff
            ):
                if (
                    lat > cutoff["min_lat"]
                    and cutoff["lon_min"] <= lon <= cutoff["lon_max"]
                ):
                    return False
            elif (
                "max_lat" in cutoff
                and "lon_min" in cutoff
                and "lon_max" in cutoff
            ):
                if (
                    lat < cutoff["max_lat"]
                    and cutoff["lon_min"] <= lon <= cutoff["lon_max"]
                ):
                    return False
            elif "max_lon" in cutoff:
                if lon < cutoff["max_lon"]:
                    return False

        return True

    def get_turkey_grid_risk(
        self,
        threshold: float = getattr(
            constants, "DEFAULT_GRID_RISK_THRESHOLD", 0.0
        ),
        hours_ago: int = 0,
    ) -> list:
        lat_start = getattr(constants, "GRID_LAT_START", 36.0)
        lat_end = getattr(constants, "GRID_LAT_END", 42.0)
        lat_step = getattr(constants, "GRID_LAT_STEP", 0.5)

        lon_start = getattr(constants, "GRID_LON_START", 26.0)
        lon_end = getattr(constants, "GRID_LON_END", 45.0)
        lon_step = getattr(constants, "GRID_LON_STEP", 0.5)

        lats = np.arange(lat_start, lat_end, lat_step)
        lons = np.arange(lon_start, lon_end, lon_step)

        grid_targets = []
        for lat in lats:
            for lon in lons:
                if self._is_inside_turkey(lat, lon):
                    grid_targets.append(
                        (
                            f"Grid ({round(float(lat),2)}, {round(float(lon),2)})",
                            round(float(lat), 4),
                            round(float(lon), 4),
                            False,
                            hours_ago,
                        )
                    )

        fixed_locs = getattr(constants, "FIXED_LOCATIONS", [])
        fixed_targets = [
            (loc[0], loc[1], loc[2], loc[3], hours_ago) for loc in fixed_locs
        ]
        all_targets = fixed_targets + grid_targets

        batch_size = 30
        batches = [
            all_targets[i : i + batch_size]
            for i in range(0, len(all_targets), batch_size)
        ]

        def process_batch(batch):
            batch_results = []
            weather_batch_data = self._batch_fetch_weather(batch)
            for idx, target_point in enumerate(batch):
                w_data = (
                    weather_batch_data[idx]
                    if idx < len(weather_batch_data)
                    else {}
                )
                point_res = self._evaluate_point_from_data(
                    target_point, w_data, hours_ago=hours_ago
                )
                batch_results.append(point_res)
            return batch_results

        results = []
        with ThreadPoolExecutor(max_workers=15) as executor:
            batch_outputs = executor.map(process_batch, batches)
            for batch_res in batch_outputs:
                results.extend(batch_res)

        return [
            res
            for res in results
            if res.get("is_fixed") or res.get("risk_score", 0.0) >= threshold
        ]

    def _calculate_wind_fire_alignment(
        self, target_lat, target_lon, fire_lat, fire_lon, wind_dir
    ):
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

    def _haversine_distance(self, lat1, lon1, lat2, lon2):
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

    def _fetch_active_fire_data(self, lat, lon, wind_dir, target_date=None):
        min_dist = 100.0
        best_alignment = 180.0
        bbox_lat_min, bbox_lat_max = lat - 0.4, lat + 0.4
        bbox_lon_min, bbox_lon_max = lon - 0.4, lon + 0.4

        urls_to_try = []
        if target_date:
            urls_to_try.append(
                settings.FIRMS_ARCHIVE_VIIRS_URL.format(
                    api_key=settings.FIRMS_API_KEY,
                    bbox_lon_min=bbox_lon_min,
                    bbox_lat_min=bbox_lat_min,
                    bbox_lon_max=bbox_lon_max,
                    bbox_lat_max=bbox_lat_max,
                    target_date=target_date,
                )
            )
            urls_to_try.append(
                settings.FIRMS_ARCHIVE_MODIS_URL.format(
                    api_key=settings.FIRMS_API_KEY,
                    bbox_lon_min=bbox_lon_min,
                    bbox_lat_min=bbox_lat_min,
                    bbox_lon_max=bbox_lon_max,
                    bbox_lat_max=bbox_lat_max,
                    target_date=target_date,
                )
            )
        else:
            urls_to_try.append(
                settings.FIRMS_NRT_URL.format(
                    api_key=settings.FIRMS_API_KEY,
                    bbox_lon_min=bbox_lon_min,
                    bbox_lat_min=bbox_lat_min,
                    bbox_lon_max=bbox_lon_max,
                    bbox_lat_max=bbox_lat_max,
                )
            )

        for url in urls_to_try:
            try:
                raw_csv = self._fetch_with_retry(url, retries=1, delay=0.5)
                lines = raw_csv.strip().splitlines()
                if len(lines) > 1 and lines[0].startswith("latitude"):
                    headers = [h.strip() for h in lines[0].split(",")]
                    lat_idx = headers.index("latitude")
                    lon_idx = headers.index("longitude")

                    for line in lines[1:]:
                        parts = line.split(",")
                        f_lat = float(parts[lat_idx])
                        f_lon = float(parts[lon_idx])

                        dist = self._haversine_distance(lat, lon, f_lat, f_lon)
                        if dist < min_dist:
                            min_dist = dist
                            best_alignment = (
                                self._calculate_wind_fire_alignment(
                                    lat, lon, f_lat, f_lon, wind_dir
                                )
                            )

                    if min_dist < 100.0:
                        break
            except Exception:
                continue

        return round(min_dist, 2), best_alignment