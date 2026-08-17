FEATURE_COLUMNS = [
    "Temperature", "RH", "Ws", "Wind_Direction", "Rain", "Rain_3D_Sum",
    "Rain_7D_Sum", "Temp_3D_Max", "RH_3D_Mean", "Dryness_Index", "VPD",
    "Surface_Temp", "Soil_Temp", "Soil_Moisture", "Dew_Point", "Pressure",
    "Evapotranspiration", "is_day", "month_sin", "month_cos", "hour_sin",
    "hour_cos", "NDVI", "Fuel_Type_Conifer", "Resin_Ignition_Potential",
    "Nearest_Fire_Dist_KM", "Wind_Fire_Vector_Alignment"
]

# Fixed monitoring locations across Turkey
FIXED_LOCATIONS = [
    ("Canakkale / Gelibolu", 40.4100, 26.6700, True),
    ("Canakkale / Kazdaglari", 39.7000, 26.8300, True),
    ("Balikesir / Edremit", 39.5900, 27.0200, True),
    ("Balikesir / Ayvalik", 39.3200, 26.6900, True),
    ("Izmir / Dikili", 39.0700, 26.8900, True),
    ("Izmir / Foca", 38.6700, 26.7500, True),
    ("Izmir / Cesme", 38.2800, 26.3700, True),
    ("Izmir / Seferihisar", 38.1969, 26.8383, True),
    ("Manisa / Spil Mountain", 38.5500, 27.4500, True),
    ("Aydin / Kusadasi", 37.8579, 27.2610, True),
    ("Aydin / Dilek Peninsula", 37.6700, 27.1600, True),
    ("Mugla / Milas", 37.3100, 27.7800, True),
    ("Mugla / Bodrum", 37.0344, 27.4305, True),
    ("Mugla / Datca", 36.7225, 27.6853, True),
    ("Mugla / Marmaris", 36.8550, 28.2742, True),
    ("Mugla / Dalaman", 36.7600, 28.8000, True),
    ("Mugla / Fethiye", 36.6200, 29.1100, True),
    ("Antalya / Kas", 36.2000, 29.6380, True),
    ("Antalya / Kumluca", 36.3700, 30.2800, True),
    ("Antalya / Kemer", 36.5986, 30.5603, True),
    ("Antalya / Manavgat", 36.7869, 31.4442, True),
    ("Antalya / Alanya", 36.5438, 31.9998, True),
    ("Mersin / Anamur", 36.0753, 32.8369, True),
    ("Mersin / Silifke", 36.3778, 33.9344, True),
    ("Adana / Kozan", 37.4500, 35.8100, True),
    ("Hatay / Belen", 36.4800, 36.2000, True),
    ("Bursa / Uludag", 40.0700, 29.1300, True),
    ("Istanbul / Belgrad Forest", 41.1800, 28.9800, True),
    ("Kocaeli / Kartepe", 40.6700, 30.0200, True),
    ("Bolu / Abant", 40.6100, 31.2800, True),
    ("Kastamonu / Cide", 41.8900, 32.9000, True),
    ("Sinop / Ayancik", 41.9400, 34.5800, True),
    ("Trabzon / Macka", 40.8100, 39.6000, True),
    ("Denizli / Honaz", 37.7600, 29.2700, True),
    ("Isparta / Egirdir", 37.8700, 30.8500, True),
    ("Ankara / Kizilcahamam", 40.4700, 32.6500, True),
    ("Tunceli / Center", 39.1000, 39.5400, True)
]

TURKEY_LAT_MIN = 35.81
TURKEY_LAT_MAX = 42.10
TURKEY_LON_MIN = 25.66
TURKEY_LON_MAX = 44.82

GRID_LAT_START = 36.0
GRID_LAT_END = 42.1
GRID_LAT_STEP = 0.3
GRID_LON_START = 26.1
GRID_LON_END = 44.5
GRID_LON_STEP = 0.3

TURKEY_SEA_MASK_CUTOFFS = [
    {"max_lat": 37.10, "min_lon": 38.80},
    {"max_lat": 36.60, "min_lon": 37.00},
    {"min_lat": 41.80, "lon_min": 28.5, "lon_max": 41.5},
    {"max_lat": 36.10, "lon_min": 28.0, "lon_max": 35.5},
    {"max_lon": 26.30},
]

MEDITERRANEAN_REGIONS = [
    {"lat_min": 30.0, "lat_max": 45.0, "lon_min": -10.0, "lon_max": 40.0},
    {"lat_min": 32.0, "lat_max": 42.0, "lon_min": -125.0, "lon_max": -115.0},
    {"lat_min": -35.0, "lat_max": -30.0, "lon_min": -73.0, "lon_max": -69.0},
]

EARTH_RADIUS_KM = 6371.0
FIRMS_BBOX_LAT_OFFSET = 0.4
FIRMS_BBOX_LON_OFFSET = 0.4

DEFAULT_MIN_FIRE_DIST_KM = 100.0
DEFAULT_BEST_ALIGNMENT_DEG = 180.0
DEFAULT_GRID_RISK_THRESHOLD = 30.0

LOW_RISK_THRESHOLD = 30.0
MEDIUM_RISK_THRESHOLD = 65.0

DRYNESS_EPSILON = 1e-5

HOURLY_WINDOW_3D = 72
HOURLY_WINDOW_7D = 168
MONTHS_IN_YEAR = 12
HOURS_IN_DAY = 24

DEFAULT_TEMPERATURE = 20.0
DEFAULT_HUMIDITY = 50.0
DEFAULT_WIND_SPEED = 0.0
DEFAULT_WIND_DIRECTION = 0.0
DEFAULT_RAIN = 0.0
DEFAULT_IS_DAY = 1
DEFAULT_SOIL_MOISTURE = 0.0
DEFAULT_DEW_POINT = 10.0
DEFAULT_SURFACE_PRESSURE = 1013.25
DEFAULT_EVAPOTRANSPIRATION = 0.0

FALLBACK_RISK_SCORE = 20.0
FALLBACK_TEMPERATURE = 25.0
FALLBACK_HUMIDITY = 40.0
FALLBACK_WIND_SPEED = 10.0

MEDITERRANEAN_NDVI = 0.60
MEDITERRANEAN_FUEL_CONIFER = 0.85
DEFAULT_NDVI = 0.40
DEFAULT_FUEL_CONIFER = 0.15

HTTP_USER_AGENT = "Mozilla/5.0"
HTTP_TIMEOUT_SECONDS = 3.0
MAX_EXECUTOR_WORKERS = 15