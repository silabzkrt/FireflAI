from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional

class DispatchPlanRequest(BaseModel):
    detection_id: int
    prediction_hours: int = Field(3, ge=1, le=72)
    wind_speed: float = Field(15.0, ge=0.0)
    wind_direction: float = Field(180.0, ge=0.0, le=360.0)
    incident_caption: Optional[str] = "Ormanlık alanda rüzgar etkisiyle hızla yayılan aktif yangın sahası."
    available_forces: Optional[str] = "2 Amfibik Uçak, 4 Helikopter, 12 Arazöz, 2 Dozer, 50 Personel"

class DispatchPlanResponse(BaseModel):
    detection_id: int
    prediction_hours: int
    spread_area_geojson: Dict[str, Any]
    tactical_order: Optional[str] = None
    nearest_water_sources: Optional[List[Dict[str, Any]]] = None
    threatened_facilities: Optional[List[Dict[str, Any]]] = None