from datetime import datetime, timezone
import re
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from database.session import Base


class FireDetection(Base):
    __tablename__ = "fire_detections"

    id = Column(Integer, primary_key=True, index=True)
    class_name = Column(String(50), nullable=False)
    confidence = Column(Float, nullable=False)
    
    latitude = Column(Float, nullable=True, index=True)
    longitude = Column(Float, nullable=True, index=True)
    
    detection_point = Column(String(100), nullable=True)
    captured_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)

    spread_polygons = relationship("FireSpreadPolygon", back_populates="detection")
    dispatch_plans = relationship("TacticalDispatchPlan", back_populates="detection")

    @property
    def parsed_latitude(self) -> float:
        if self.latitude is not None:
            return float(self.latitude)
        if self.detection_point:
            match = re.search(r"POINT\(([-+]?\d*\.?\d+)\s+([-+]?\d*\.?\d+)\)", self.detection_point)
            if match:
                return float(match.group(2))
        return 0.0

    @property
    def parsed_longitude(self) -> float:
        if self.longitude is not None:
            return float(self.longitude)
        if self.detection_point:
            match = re.search(r"POINT\(([-+]?\d*\.?\d+)\s+([-+]?\d*\.?\d+)\)", self.detection_point)
            if match:
                return float(match.group(1))
        return 0.0


class MeteorologicalRisk(Base):
    __tablename__ = "meteorological_risks"

    id = Column(Integer, primary_key=True, index=True)
    risk_level = Column(Float, nullable=False)
    
    latitude = Column(Float, nullable=True, index=True)
    longitude = Column(Float, nullable=True, index=True)
    
    temperature = Column(Float, nullable=True)
    humidity = Column(Float, nullable=True)
    wind_speed = Column(Float, nullable=True)
    wind_direction = Column(Float, nullable=True)
    
    risk_point = Column(String(100), nullable=False)
    captured_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)


class FireSpreadPolygon(Base):
    __tablename__ = "fire_spread_polygons"

    id = Column(Integer, primary_key=True, index=True)
    fire_detection_id = Column(Integer, ForeignKey("fire_detections.id", ondelete="SET NULL"), nullable=True, index=True)
    
    latitude = Column(Float, nullable=True, index=True)
    longitude = Column(Float, nullable=True, index=True)
    
    spread_area = Column(Text, nullable=False)
    wind_direction = Column(Float, nullable=True)
    wind_speed = Column(Float, nullable=True)
    prediction_hours = Column(Integer, nullable=True)
    spread_probability = Column(Float, nullable=True)
    affected_area_hectares = Column(Float, nullable=True)
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)

    detection = relationship("FireDetection", back_populates="spread_polygons")


class TacticalDispatchPlan(Base):
    __tablename__ = "tactical_dispatch_plans"

    id = Column(Integer, primary_key=True, index=True)
    fire_detection_id = Column(Integer, ForeignKey("fire_detections.id", ondelete="SET NULL"), nullable=True, index=True)
    
    latitude = Column(Float, nullable=True, index=True)
    longitude = Column(Float, nullable=True, index=True)
    
    incident_caption = Column(String(500), nullable=True)
    available_forces = Column(String(500), nullable=True)
    tactical_order = Column(Text, nullable=False)
    
    spread_area_wkt = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)

    detection = relationship("FireDetection", back_populates="dispatch_plans")