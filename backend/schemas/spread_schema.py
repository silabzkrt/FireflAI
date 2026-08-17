from pydantic import BaseModel, Field
from typing import Any, Dict, Optional

class SpreadPredictionRequest(BaseModel):
    detection_id: int
    prediction_hours: int = Field(24, ge=1, le=72)
    wind_speed: float = Field(15.0, ge=0.0)
    wind_direction: float = Field(180.0, ge=0.0, le=360.0)
    slope: Optional[float] = 0.0
    vegetation_density: Optional[float] = 0.6

class SpreadPredictionResponse(BaseModel):
    detection_id: int
    prediction_hours: int
    spread_area_geojson: Dict[str, Any]
    spread_probability: float
    affected_area_hectares: float