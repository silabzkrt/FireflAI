from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
import traceback

from database.session import get_db
from database.models import FireDetection, FireSpreadPolygon
from schemas.spread_schema import SpreadPredictionRequest, SpreadPredictionResponse
from services.spread_service import FireSpreadService

router = APIRouter()
spread_service = FireSpreadService()


@router.post("/predict-spread", response_model=SpreadPredictionResponse)
async def predict_spread(
    payload: SpreadPredictionRequest,
    db: Session = Depends(get_db)
):
    detection = None
    if payload.detection_id:
        detection = db.query(FireDetection).filter(FireDetection.id == payload.detection_id).first()

    lat = None
    lon = None

    if detection:
        lat = getattr(detection, "latitude", None) or getattr(detection, "parsed_latitude", None)
        lon = getattr(detection, "longitude", None) or getattr(detection, "parsed_longitude", None)

    if lat is None and getattr(payload, "latitude", None) is not None:
        lat = payload.latitude
    if lon is None and getattr(payload, "longitude", None) is not None:
        lon = payload.longitude

    # fallback
    if lat is None:
        lat = 36.8550
    if lon is None:
        lon = 28.2742

    lat = float(lat)
    lon = float(lon)

    if detection and (getattr(detection, "latitude", None) is None or getattr(detection, "longitude", None) is None):
        try:
            if hasattr(detection, "latitude") and detection.latitude is None:
                detection.latitude = lat
            if hasattr(detection, "longitude") and detection.longitude is None:
                detection.longitude = lon
            db.commit()
        except Exception:
            db.rollback()

    try:
        spread_geojson, prob, area_ha = spread_service.predict_spread(
            lat=lat,
            lon=lon,
            wind_speed=payload.wind_speed,
            wind_direction=payload.wind_direction,
            hours=payload.prediction_hours,
            slope=getattr(payload, "slope", 0.0),
            vegetation_density=getattr(payload, "vegetation_density", 0.6)
        )

        polygon_coords = spread_geojson['coordinates'][0]
        coord_strings = [f"{c[0]} {c[1]}" for c in polygon_coords]
        polygon_wkt = f"SRID=4326;POLYGON(({','.join(coord_strings)}))"

        fire_det_id = detection.id if detection else payload.detection_id

        new_polygon = FireSpreadPolygon(
            fire_detection_id=fire_det_id,
            spread_area=polygon_wkt,
            wind_speed=payload.wind_speed,
            wind_direction=payload.wind_direction,
            prediction_hours=payload.prediction_hours,
            spread_probability=prob,
            affected_area_hectares=area_ha
        )
        db.add(new_polygon)
        db.commit()

        return SpreadPredictionResponse(
            detection_id=fire_det_id,
            prediction_hours=payload.prediction_hours,
            spread_area_geojson=spread_geojson,
            spread_probability=prob,
            affected_area_hectares=area_ha
        )

    except Exception as e:
        db.rollback()
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Yayılım tahmini başarısız: {str(e)}")


@router.get("/history")
def get_spread_history(
    limit: int = Query(50, description="Getirilecek kayıt sayısı (N adet)"),
    detection_id: Optional[int] = Query(None, description="Opsiyonel: Sadece bu yangına ait olanları filtrele"),
    db: Session = Depends(get_db)
):
    query = db.query(FireSpreadPolygon)
    if detection_id is not None:
        query = query.filter(FireSpreadPolygon.fire_detection_id == detection_id)
        
    spreads = query.order_by(FireSpreadPolygon.created_at.desc()).limit(limit).all()

    results = []
    for s in spreads:
        results.append({
            "id": s.id,
            "fire_detection_id": s.fire_detection_id,
            "spread_area": s.spread_area,
            "wind_direction": s.wind_direction,
            "wind_speed": s.wind_speed,
            "prediction_hours": s.prediction_hours,
            "spread_probability": s.spread_probability,
            "affected_area_hectares": s.affected_area_hectares,
            "created_at": s.created_at.isoformat() if s.created_at else None
        })
    return results


@router.get("/{spread_id}")
def get_spread_by_id(spread_id: int, db: Session = Depends(get_db)):
    s = db.query(FireSpreadPolygon).filter(FireSpreadPolygon.id == spread_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Yayılım kaydı bulunamadı.")

    return {
        "id": s.id,
        "fire_detection_id": s.fire_detection_id,
        "spread_area": s.spread_area,
        "wind_direction": s.wind_direction,
        "wind_speed": s.wind_speed,
        "prediction_hours": s.prediction_hours,
        "spread_probability": s.spread_probability,
        "affected_area_hectares": s.affected_area_hectares,
        "created_at": s.created_at.isoformat() if s.created_at else None
    }


@router.get("/by-detection/{detection_id}")
def get_spreads_by_detection(detection_id: int, db: Session = Depends(get_db)):
    spreads = (
        db.query(FireSpreadPolygon)
        .filter(FireSpreadPolygon.fire_detection_id == detection_id)
        .order_by(FireSpreadPolygon.created_at.desc())
        .all()
    )
    
    return [
        {
            "id": s.id,
            "fire_detection_id": s.fire_detection_id,
            "spread_area": s.spread_area,
            "wind_direction": s.wind_direction,
            "wind_speed": s.wind_speed,
            "prediction_hours": s.prediction_hours,
            "spread_probability": s.spread_probability,
            "affected_area_hectares": s.affected_area_hectares,
            "created_at": s.created_at.isoformat() if s.created_at else None
        }
        for s in spreads
    ]