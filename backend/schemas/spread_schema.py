"""
FireflAI - Wildfire Spread Pydantic Schemas

Defines request and response schemas for ML-based wildfire propagation simulations,
including environmental input parameters, GeoJSON spread polygons, and burn area metrics.
"""

from pydantic import BaseModel, Field
from typing import Any, Dict, Optional

class SpreadPredictionRequest(BaseModel):
    detection_id: Optional[int] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    prediction_hours: int = Field(6, ge=1, le=72)
    wind_speed: float = Field(15.0, ge=0.0)
    wind_direction: float = Field(180.0, ge=0.0, le=360.0)
    slope: Optional[float] = 5.0
    vegetation_density: Optional[float] = 0.7

class SpreadPredictionResponse(BaseModel):
    id: Optional[int] = None
    detection_id: Optional[int] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    prediction_hours: int
    spread_area_geojson: Dict[str, Any]
    spread_probability: float
    affected_area_hectares: float