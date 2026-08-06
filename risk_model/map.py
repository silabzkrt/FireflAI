from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import json
import math
import os
import time
import urllib.error
import urllib.request
import folium
import joblib
import numpy as np
import pandas as pd

FIRMS_API_KEY = "8d3885d51beedbbbbd8ed506bb0ff510"
FIRMS_API_URL = "https://firms.modaps.eosdis.nasa.gov/api/area/csv/{api_key}/VIIRS_SNPP_NRT/{bbox_lon_min:.2f},{bbox_lat_min:.2f},{bbox_lon_max:.2f},{bbox_lat_max:.2f}/1"
WEATHER_API_URL = (
    "https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
    "&current=temperature_2m,relative_humidity_2m,rain,wind_speed_10m,wind_direction_10m,is_day,"
    "surface_temperature,soil_temperature_0_to_10cm,soil_moisture_0_to_10cm,dew_point_2m,surface_pressure,et0_fao_evapotranspiration"
    "&hourly=rain,temperature_2m,relative_humidity_2m&past_days=3&timezone=auto"
)
MAP_TILES_URL = "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"

DYNAMIC_GRID_THRESHOLD = 60
OUTPUT_HTML_FILE = "turkey_map.html"
MODEL_FILENAME = "production_fire_model_xgboost.joblib"

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(SCRIPT_DIR, MODEL_FILENAME)

try:
    model = joblib.load(MODEL_PATH)
except Exception as e:
    raise RuntimeError(f"Failed to load model from {MODEL_PATH}: {e}")

FEATURE_COLUMNS = [
    "Temperature", "RH", "Ws", "Wind_Direction", "Rain", "Rain_3D_Sum",
    "Rain_7D_Sum", "Temp_3D_Max", "RH_3D_Mean", "Dryness_Index", "VPD",
    "Surface_Temp", "Soil_Temp", "Soil_Moisture", "Dew_Point", "Pressure",
    "Evapotranspiration", "is_day", "month_sin", "month_cos", "hour_sin",
    "hour_cos", "NDVI", "Fuel_Type_Conifer", "Resin_Ignition_Potential",
    "Nearest_Fire_Dist_KM", "Wind_Fire_Vector_Alignment"
]

FIXED_LOCATIONS = [
    ("Çanakkale / Gelibolu", 40.4100, 26.6700, True),
    ("Çanakkale / Kazdağları", 39.7000, 26.8300, True),
    ("Balıkesir / Edremit", 39.5900, 27.0200, True),
    ("Balıkesir / Ayvalık", 39.3200, 26.6900, True),
    ("İzmir / Dikili", 39.0700, 26.8900, True),
    ("İzmir / Foça", 38.6700, 26.7500, True),
    ("İzmir / Çeşme", 38.2800, 26.3700, True),
    ("İzmir / Seferihisar", 38.1969, 26.8383, True),
    ("Manisa / Spil Dağı", 38.5500, 27.4500, True),
    ("Aydın / Kuşadası", 37.8579, 27.2610, True),
    ("Aydın / Dilek Yarımadası", 37.6700, 27.1600, True),
    ("Muğla / Milas", 37.3100, 27.7800, True),
    ("Muğla / Bodrum", 37.0344, 27.4305, True),
    ("Muğla / Datça", 36.7225, 27.6853, True),
    ("Muğla / Marmaris", 36.8550, 28.2742, True),
    ("Muğla / Dalaman", 36.7600, 28.8000, True),
    ("Muğla / Fethiye", 36.6200, 29.1100, True),
    ("Antalya / Kaş", 36.2000, 29.6380, True),
    ("Antalya / Kumluca", 36.3700, 30.2800, True),
    ("Antalya / Kemer", 36.5986, 30.5603, True),
    ("Antalya / Manavgat", 36.7869, 31.4442, True),
    ("Antalya / Alanya", 36.5438, 31.9998, True),
    ("Mersin / Anamur", 36.0753, 32.8369, True),
    ("Mersin / Silifke", 36.3778, 33.9344, True),
    ("Adana / Kozan", 37.4500, 35.8100, True),
    ("Hatay / Belen", 36.4800, 36.2000, True),
    ("Bursa / Uludağ", 40.0700, 29.1300, True),
    ("İstanbul / Belgrad Ormanı", 41.1800, 28.9800, True),
    ("Kocaeli / Kartepe", 40.6700, 30.0200, True),
    ("Bolu / Abant", 40.6100, 31.2800, True),
    ("Kastamonu / Cide", 41.8900, 32.9000, True),
    ("Sinop / Ayancık", 41.9400, 34.5800, True),
    ("Trabzon / Maçka", 40.8100, 39.6000, True),
    ("Denizli / Honaz", 37.7600, 29.2700, True),
    ("Isparta / Eğirdir", 37.8700, 30.8500, True),
    ("Ankara / Kızılcahamam", 40.4700, 32.6500, True),
    ("Dersim / Tunceli", 39.1000, 39.5400, True)
]

def fetch_with_retry(url, retries=2, delay=0.5):
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=3.0) as response:
                return json.loads(response.read().decode())
        except Exception:
            if attempt < retries - 1:
                time.sleep(delay)
                continue
    return {}

def calculate_vpd(temp, rh):
    svp = 0.61078 * np.exp((17.27 * temp) / (temp + 237.3))
    avp = svp * (rh / 100.0)
    return round(float(svp - avp), 4)

def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def calculate_wind_fire_alignment(target_lat, target_lon, fire_lat, fire_lon, wind_dir):
    dlon = math.radians(target_lon - fire_lon)
    lat1, lat2 = math.radians(fire_lat), math.radians(target_lat)
    x = math.sin(dlon) * math.cos(lat2)
    y = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(dlon)
    bearing = (math.degrees(math.atan2(x, y)) + 360) % 360
    wind_push_dir = (wind_dir + 180) % 360
    angle_diff = abs(wind_push_dir - bearing)
    if angle_diff > 180:
        angle_diff = 360 - angle_diff
    return round(angle_diff, 1)

def fetch_auto_active_fire_data(lat, lon, wind_dir):
    min_dist = 100.0
    best_alignment = 180.0
    bbox_lat_min, bbox_lat_max = lat - 0.4, lat + 0.4
    bbox_lon_min, bbox_lon_max = lon - 0.4, lon + 0.4

    firms_url = FIRMS_API_URL.format(
        api_key=FIRMS_API_KEY,
        bbox_lon_min=bbox_lon_min,
        bbox_lat_min=bbox_lat_min,
        bbox_lon_max=bbox_lon_max,
        bbox_lat_max=bbox_lat_max
    )

    try:
        req = urllib.request.Request(firms_url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=2.5) as response:
            lines = response.read().decode("utf-8").strip().splitlines()
            if len(lines) > 1:
                headers = [h.strip() for h in lines[0].split(",")]
                lat_idx, lon_idx = headers.index("latitude"), headers.index("longitude")
                for line in lines[1:]:
                    parts = line.split(",")
                    f_lat, f_lon = float(parts[lat_idx]), float(parts[lon_idx])
                    dist = haversine_distance(lat, lon, f_lat, f_lon)
                    if dist < min_dist:
                        min_dist = dist
                        best_alignment = calculate_wind_fire_alignment(lat, lon, f_lat, f_lon, wind_dir)
    except Exception:
        pass

    return round(min_dist, 2), best_alignment

def is_inside_turkey(lat, lon):
    if lat < 35.81 or lat > 42.10:
        return False
    if lon < 25.66 or lon > 44.82:
        return False
    if lat < 37.10 and lon > 38.80:
        return False
    if lat < 36.60 and lon > 37.00:
        return False
    if lat > 41.80 and (28.5 <= lon <= 41.5):
        return False
    if lat < 36.10 and (28.0 <= lon <= 35.5):
        return False
    if lon < 26.30:
        return False
    return True

def evaluate_point_risk(point_info):
    name, lat, lon, is_fixed = point_info
    
    is_mediterranean = (35.8 <= lat <= 41.5) and (26.0 <= lon <= 37.0)
    ndvi = 0.65 if is_mediterranean else 0.35
    fuel_conifer = 0.85 if is_mediterranean else 0.20

    api_url = WEATHER_API_URL.format(lat=lat, lon=lon)

    try:
        data = fetch_with_retry(api_url)
        current = data.get("current", {})
        hourly = data.get("hourly", {})

        live_temp = float(current.get("temperature_2m") or 25.0)
        live_rh = float(current.get("relative_humidity_2m") or 40.0)
        live_ws = float(current.get("wind_speed_10m") or 10.0)
        live_wdir = float(current.get("wind_direction_10m") or 180.0)
        live_rain = float(current.get("rain") or 0.0)
        is_day = int(current.get("is_day", 1))

        now = datetime.now()
        month_int, hour_int = now.month, now.hour

        surf_temp = float(current.get("surface_temperature") or live_temp)
        soil_temp = float(current.get("soil_temperature_0_to_10cm") or live_temp)
        soil_moist = float(current.get("soil_moisture_0_to_10cm") or 0.1)
        dew_point = float(current.get("dew_point_2m") or 12.0)
        pressure = float(current.get("surface_pressure") or 1013.0)
        evap = float(current.get("et0_fao_evapotranspiration") or 1.0)

        past_rains = [float(r) if r is not None else 0.0 for r in hourly.get("rain", [])]
        past_temps = [float(t) if t is not None else live_temp for t in hourly.get("temperature_2m", [])]
        past_rhs = [float(h) if h is not None else live_rh for h in hourly.get("relative_humidity_2m", [])]

        rain_3d_sum = round(sum(past_rains[-72:]), 2) if past_rains else 0.0
        rain_7d_sum = rain_3d_sum
        temp_3d_max = round(max(past_temps[-72:]), 2) if past_temps else live_temp
        rh_3d_mean = round(float(np.mean(past_rhs[-72:])), 2) if past_rhs else live_rh

        live_dryness = float(live_temp / (live_rh + 1e-5))
        vpd = calculate_vpd(live_temp, live_rh)
        resin_potential = round((live_temp / (live_rh + 1.0)) * fuel_conifer * ndvi, 4)

        month_sin = round(float(np.sin(2 * np.pi * month_int / 12)), 4)
        month_cos = round(float(np.cos(2 * np.pi * month_int / 12)), 4)
        hour_sin = round(float(np.sin(2 * np.pi * hour_int / 24)), 4)
        hour_cos = round(float(np.cos(2 * np.pi * hour_int / 24)), 4)

        nearest_fire_dist, vector_align = fetch_auto_active_fire_data(lat, lon, live_wdir)

        input_dict = {
            "Temperature": [live_temp], "RH": [live_rh], "Ws": [live_ws], "Wind_Direction": [live_wdir],
            "Rain": [live_rain], "Rain_3D_Sum": [rain_3d_sum], "Rain_7D_Sum": [rain_7d_sum],
            "Temp_3D_Max": [temp_3d_max], "RH_3D_Mean": [rh_3d_mean], "Dryness_Index": [live_dryness],
            "VPD": [vpd], "Surface_Temp": [surf_temp], "Soil_Temp": [soil_temp], "Soil_Moisture": [soil_moist],
            "Dew_Point": [dew_point], "Pressure": [pressure], "Evapotranspiration": [evap], "is_day": [is_day],
            "month_sin": [month_sin], "month_cos": [month_cos], "hour_sin": [hour_sin], "hour_cos": [hour_cos],
            "NDVI": [ndvi], "Fuel_Type_Conifer": [fuel_conifer], "Resin_Ignition_Potential": [resin_potential],
            "Nearest_Fire_Dist_KM": [nearest_fire_dist], "Wind_Fire_Vector_Alignment": [vector_align]
        }

        input_df = pd.DataFrame(input_dict)[FEATURE_COLUMNS]
        score = round(float(model.predict_proba(input_df)[:, 1][0] * 100), 2)
        
        return {
            "name": name, "lat": lat, "lon": lon, "score": score,
            "temp": live_temp, "rh": live_rh, "ws": live_ws,
            "is_fixed": is_fixed
        }

    except Exception:
        return {
            "name": name, "lat": lat, "lon": lon, "score": 20.0,
            "temp": 25.0, "rh": 40.0, "ws": 10.0,
            "is_fixed": is_fixed
        }

def generate_grid_locations():
    lats_dense = np.arange(36.0, 42.1, 0.22)
    lons_dense = np.arange(26.1, 44.5, 0.22)
    grid_locations = []
    for lat in lats_dense:
        for lon in lons_dense:
            if is_inside_turkey(lat, lon):
                grid_locations.append((f"Grid ({round(lat,2)}, {round(lon,2)})", round(lat, 4), round(lon, 4), False))
    return grid_locations

def create_map(final_render_points):
    m = folium.Map(
        location=[38.8, 32.0],
        zoom_start=6,
        tiles=MAP_TILES_URL,
        attr='&copy; OpenStreetMap &copy; CARTO'
    )

    raw_heat_data = [[res["lat"], res["lon"], res["score"] / 100.0] for res in final_render_points]

    for res in final_render_points:
        score = res["score"]
        if score >= 90:
            badge_color = "#e74c3c"
            risk_label = "KRİTİK YÜKSEK"
        elif score >= 80:
            badge_color = "#e67e22"
            risk_label = "YÜKSEK"
        elif score >= 60:
            badge_color = "#f1c40f"
            risk_label = "ORTA"
        elif score >= 40:
            badge_color = "#a3e635"
            risk_label = "DÜŞÜK-ORTA"
        else:
            badge_color = "#2ecc71"
            risk_label = "DÜŞÜK"

        popup_html = f"""
        <div style="font-family: Arial, sans-serif; width: 180px; padding: 2px;">
            <h4 style="margin: 0 0 5px 0; color: #333; font-size: 14px;">{res['name']}</h4>
            <div style="background-color: {badge_color}; color: white; padding: 4px 8px; border-radius: 4px; font-weight: bold; font-size: 13px; text-align: center; margin-bottom: 8px;">
                Risk: %{score} ({risk_label})
            </div>
            <div style="font-size: 12px; color: #555; line-height: 1.4;">
                <b>Sıcaklık:</b> {res['temp']}°C<br>
                <b>Nem:</b> %{res['rh']}<br>
                <b>Rüzgar:</b> {res['ws']} km/h
            </div>
        </div>
        """

        folium.CircleMarker(
            location=[res["lat"], res["lon"]],
            radius=14,
            color="transparent",
            fill=True,
            fill_color="transparent",
            fill_opacity=0.01,
            popup=folium.Popup(popup_html, max_width=220)
        ).add_to(m)

    inject_script = f"""
    <script src="https://cdn.jsdelivr.net/npm/leaflet.heat@0.2.0/dist/leaflet-heat.js"></script>
    <script>
        window.addEventListener('load', function() {{
            setTimeout(function() {{
                var map = null;
                for (var key in window) {{
                    if (key.startsWith('map_')) {{
                        map = window[key];
                        break;
                    }}
                }}
                if (map) {{
                    var heatData = {json.dumps(raw_heat_data)};
                    L.heatLayer(heatData, {{
                        radius: 16,
                        blur: 12,
                        max: 1.0,
                        minOpacity: 0.30,
                        gradient: {{
                            0.15: '#2ecc71',
                            0.40: '#a3e635',
                            0.60: '#f1c40f',
                            0.78: '#e67e22',
                            0.90: '#e74c3c'
                        }}
                    }}).addTo(map);
                }}
            }}, 300);
        }});
    </script>
    """

    m.get_root().html.add_child(folium.Element(inject_script))
    m.save(OUTPUT_HTML_FILE)

def main():
    grid_locations = generate_grid_locations()
    all_targets = FIXED_LOCATIONS + grid_locations

    with ThreadPoolExecutor(max_workers=18) as executor:
        risk_results = list(executor.map(evaluate_point_risk, all_targets))

    final_render_points = [
        res for res in risk_results
        if res["is_fixed"] or res["score"] >= DYNAMIC_GRID_THRESHOLD
    ]

    create_map(final_render_points)

if __name__ == "__main__":
    main()