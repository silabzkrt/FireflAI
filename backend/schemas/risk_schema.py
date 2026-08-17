from typing import Optional, List
from pydantic import BaseModel, Field

class SinglePointRiskRequest(BaseModel):
    location_name: Optional[str] = Field("Unknown Location", example="Mugla / Marmaris")
    latitude: float = Field(..., example=36.8550)
    longitude: float = Field(..., example=28.2742)
    hours_ago: Optional[int] = Field(0, description="0 = Now, 6 = 6 hours ago, 24 = 1 day ago")
    target_date: Optional[str] = Field(None, example="2025-06-28", description="Optional YYYY-MM-DD for historical analysis")


class RiskReportResponse(BaseModel):
    location_name: Optional[str] = "Unknown Location"
    latitude: float
    longitude: float
    risk_score: float
    
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    rh: Optional[float] = None
    wind_speed: Optional[float] = None
    wind_direction: Optional[float] = None

    day_status: Optional[str] = None
    month: Optional[int] = None
    hour: Optional[int] = None
    real_slope: Optional[float] = None
    ndvi: Optional[float] = None
    fuel_conifer: Optional[float] = None
    resin_potential: Optional[float] = None
    nearest_fire_dist: Optional[float] = None
    vector_alignment: Optional[float] = None
    rain_3d_sum: Optional[float] = None
    rain_7d_sum: Optional[float] = None
    temp_3d_max: Optional[float] = None
    rh_3d_mean: Optional[float] = None
    soil_moisture: Optional[float] = None
    vpd: Optional[float] = None
    evapotranspiration: Optional[float] = None

    status: Optional[str] = "success"
    query_time_iso: Optional[str] = None
    captured_at: Optional[str] = None


class GridPointRiskResponse(BaseModel):
    name: str
    lat: float
    lon: float
    score: float
    temp: float
    rh: float
    ws: float
    is_fixed: bool