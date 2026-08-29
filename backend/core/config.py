"""
FireflAI - Application Configuration & Settings

Manages environment variables, external API endpoints, and credential configurations.
Defines base URLs and formats for NASA FIRMS satellite data, Open-Meteo weather and air quality APIs,
and Open-Elevation services.
"""

import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    FIRMS_API_KEY: str = os.getenv("FIRMS_API_KEY", "e51623bd04cdb9f80855b5b27eb3be30")

    FIRMS_NRT_URL: str = (
        "https://firms.modaps.eosdis.nasa.gov/api/area/csv/{api_key}/"
        "VIIRS_SNPP_NRT/{bbox_lon_min:.2f},{bbox_lat_min:.2f},"
        "{bbox_lon_max:.2f},{bbox_lat_max:.2f}/1"
    )
    FIRMS_ARCHIVE_VIIRS_URL: str = (
        "https://firms.modaps.eosdis.nasa.gov/api/area/csv/{api_key}/"
        "VIIRS_SNPP_SP/{bbox_lon_min:.2f},{bbox_lat_min:.2f},"
        "{bbox_lon_max:.2f},{bbox_lat_max:.2f}/1/{target_date}"
    )
    FIRMS_ARCHIVE_MODIS_URL: str = (
        "https://firms.modaps.eosdis.nasa.gov/api/area/csv/{api_key}/"
        "MODIS_SP/{bbox_lon_min:.2f},{bbox_lat_min:.2f},"
        "{bbox_lon_max:.2f},{bbox_lat_max:.2f}/1/{target_date}"
    )

    AIR_QUALITY_API_URL: str = (
        "https://air-quality-api.open-meteo.com/v1/air-quality?"
        "latitude={lat}&longitude={lon}&current=pm2_5"
    )
    WEATHER_API_URL: str = (
        "https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
        "&current=temperature_2m,relative_humidity_2m,rain,wind_speed_10m,"
        "wind_direction_10m,is_day,surface_temperature,soil_temperature_0_to_10cm,"
        "soil_moisture_0_to_10cm,dew_point_2m,surface_pressure,et0_fao_evapotranspiration"
        "&hourly=rain,temperature_2m,relative_humidity_2m,wind_speed_10m,wind_direction_10m&past_days=7&timezone=auto"
    )
    ELEVATION_API_URL: str = (
        "https://api.open-elevation.com/api/v1/lookup?"
        "locations={lat},{lon}|{lat_offset},{lon}"
    )

settings = Settings()