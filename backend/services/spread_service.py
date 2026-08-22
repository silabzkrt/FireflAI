import os
import math
import joblib
import numpy as np
from typing import Dict, Any, Tuple


class FireSpreadService:
    def __init__(self):
        self.model_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "models", "spread_model", "spread_model.joblib")
        )
        self.model = None
        self._load_model()

    def _load_model(self):
        if os.path.exists(self.model_path):
            try:
                self.model = joblib.load(self.model_path)
                print(f"Spread ML Modeli basariyla yuklendi: {self.model_path}")
            except Exception as e:
                print(f"Spread modeli yuklenirken hata: {e}")
                self.model = None
        else:
            print(f"Uyari: {self.model_path} bulunamadi.")

    def predict_spread(
        self,
        lat: float,
        lon: float,
        hours: int = 24,
        wind_speed: float = 15.0,
        wind_direction: float = 180.0,
        slope: float = 0.0,
        vegetation_density: float = 0.6,
        temp: float = 32.0,
        humidity: float = 25.0,
        **kwargs,
    ) -> Tuple[Dict[str, Any], float, float]:

        if self.model is not None:
            try:
                features = np.array([[
                    float(wind_speed),
                    float(wind_direction),
                    float(temp),
                    float(humidity),
                    float(slope),
                    float(vegetation_density),
                    1.0
                ]])
                prob = float(self.model.predict_proba(features)[0][1])
                spread_probability = round(prob, 4)
            except Exception as e:
                print(f"Model tahmin hatasi: {e}")
                spread_probability = self._dynamic_fallback_prob(wind_speed, slope, vegetation_density)
        else:
            spread_probability = self._dynamic_fallback_prob(wind_speed, slope, vegetation_density)

        spread_rate_kmh = 0.05 + (wind_speed * 0.04) + (slope * 0.01) + (vegetation_density * 0.03)
        max_dist_km = spread_rate_kmh * hours
        
        semi_major_km = max_dist_km
        semi_minor_km = max_dist_km * 0.45
        affected_hectares = round(math.pi * semi_major_km * semi_minor_km * 100, 2)

        rad_wind = math.radians(wind_direction)
        coords = []
        num_points = 24

        km_to_lat = 1.0 / 111.0
        km_to_lon = 1.0 / (111.0 * math.cos(math.radians(lat)))

        for i in range(num_points + 1):
            theta = 2 * math.pi * (i / num_points)
            dx = semi_minor_km * math.cos(theta)
            dy = semi_major_km * math.sin(theta) + (semi_major_km * 0.4)

            rot_x = dx * math.cos(rad_wind) - dy * math.sin(rad_wind)
            rot_y = dx * math.sin(rad_wind) + dy * math.cos(rad_wind)

            pt_lat = lat + (rot_y * km_to_lat)
            pt_lon = lon + (rot_x * km_to_lon)
            coords.append([round(pt_lon, 6), round(pt_lat, 6)])

        geojson_polygon = {
            "type": "Polygon",
            "coordinates": [coords],
        }

        return geojson_polygon, spread_probability, affected_hectares

    calculate_spread = predict_spread

    def _dynamic_fallback_prob(self, ws: float, slope: float, veg: float) -> float:
        score = (ws / 60.0) * 0.5 + (slope / 30.0) * 0.25 + veg * 0.25
        return round(min(max(score, 0.1), 0.99), 4)


SpreadPredictionService = FireSpreadService