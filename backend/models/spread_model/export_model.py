import os
import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier

# Notebook'taki yayılım parametreleri (Rüzgar, Sıcaklık, Nem, Eğim, Bitki Örtüsü, Mevcut Yangın)
# X: [wind_speed, wind_direction, temp, humidity, slope, ndvi, is_fire_origin]
np.random.seed(42)
n_samples = 2000

wind_speed = np.random.uniform(5, 50, n_samples)
wind_dir = np.random.uniform(0, 360, n_samples)
temp = np.random.uniform(20, 45, n_samples)
humidity = np.random.uniform(10, 60, n_samples)
slope = np.random.uniform(0, 30, n_samples)
ndvi = np.random.uniform(0.1, 0.9, n_samples)
is_fire_origin = np.random.choice([0, 1], n_samples, p=[0.3, 0.7])

X = np.column_stack([wind_speed, wind_dir, temp, humidity, slope, ndvi, is_fire_origin])

# Yangın yayılım fizik kuralına dayalı hedef etiket (0: Yayılmaz, 1: Yayılır)
spread_score = (
    (wind_speed / 50.0) * 0.35 +
    (temp / 45.0) * 0.25 +
    ((100 - humidity) / 100.0) * 0.20 +
    (ndvi) * 0.10 +
    (slope / 30.0) * 0.10
)
y = (spread_score > 0.45).astype(int)

# Modeli eğit
rf = RandomForestClassifier(n_estimators=100, max_depth=8, random_state=42)
rf.fit(X, y)

# Backend models dizinine kaydet
output_dir = os.path.join("..", "backend", "models")
os.makedirs(output_dir, exist_ok=True)
output_path = os.path.join(output_dir, "spread_model.joblib")

joblib.dump(rf, output_path)
print(f"[BAŞARILI] Model kaydedildi: {os.path.abspath(output_path)}")