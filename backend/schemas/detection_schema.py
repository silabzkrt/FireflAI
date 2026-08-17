from pydantic import BaseModel, Field
from typing import List, Optional

class DetectionRequest(BaseModel):
    latitude: float
    longitude: float

class DetectionResult(BaseModel):
    class_name: str
    confidence: float
    bbox: List[float]

class DetectionResponse(BaseModel):
    detected: bool
    results: List[DetectionResult]