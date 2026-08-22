from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
import traceback

from database.session import get_db
from database.models import FireDetection, TacticalDispatchPlan
from schemas.dispatch_schema import DispatchPlanRequest, DispatchPlanResponse
from services.dispatch_service import DispatchService

router = APIRouter()
dispatch_service = DispatchService()


@router.post("/generate-plan", response_model=DispatchPlanResponse)
async def generate_plan(
    payload: DispatchPlanRequest,
    db: Session = Depends(get_db)
):
    detection = None
    if payload.detection_id:
        detection = db.query(FireDetection).filter(FireDetection.id == payload.detection_id).first()

    lat = payload.latitude if payload.latitude is not None else None
    lon = payload.longitude if payload.longitude is not None else None

    # fallback
    if (lat is None or lon is None) and detection:
        if lat is None:
            lat = getattr(detection, "latitude", None) or getattr(detection, "parsed_latitude", None)
        if lon is None:
            lon = getattr(detection, "longitude", None) or getattr(detection, "parsed_longitude", None)

    if lat is None:
        lat = 36.8550
    if lon is None:
        lon = 28.2742

    lat = float(lat)
    lon = float(lon)

    if detection:
        try:
            if hasattr(detection, "latitude"):
                detection.latitude = lat
            if hasattr(detection, "longitude"):
                detection.longitude = lon
            db.commit()
        except Exception:
            db.rollback()

    try:
        raw_order, nearest_water, nearest_settlements = dispatch_service.generate_plan(
            lat=lat,
            lon=lon,
            wind_speed=payload.wind_speed,
            caption=payload.incident_caption or f"Aktif yangın sahası. Koordinat: [{lat:.4f}°N, {lon:.4f}°E]",
            forces=payload.available_forces or "2 Amfibik Uçak, 4 Helikopter, 12 Arazöz, 2 Dozer, 50 Personel"
        )

        spread_geojson = dispatch_service.calculate_spread_polygon(
            lat=lat,
            lon=lon,
            wind_speed=payload.wind_speed,
            wind_dir=payload.wind_direction,
            hours=payload.prediction_hours
        )

        fire_det_id = detection.id if detection else payload.detection_id

        new_plan = TacticalDispatchPlan(
            fire_detection_id=fire_det_id,
            incident_caption=payload.incident_caption or "Müdahale Planı",
            available_forces=payload.available_forces or "",
            tactical_order=raw_order
        )
        db.add(new_plan)
        db.commit()

        return {
            "detection_id": fire_det_id,
            "prediction_hours": payload.prediction_hours,
            "spread_area_geojson": spread_geojson,
            "tactical_order": raw_order,
            "nearest_water_sources": nearest_water,
            "threatened_facilities": nearest_settlements
        }

    except Exception as e:
        db.rollback()
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Sevk planı oluşturulamadı: {str(e)}")


@router.get("/history")
def get_dispatch_history(
    limit: int = Query(20, description="Getirilecek plan sayısı (N adet)"),
    detection_id: Optional[int] = Query(None, description="Opsiyonel: Sadece bu yangına ait planı filtrele"),
    db: Session = Depends(get_db)
):
    query = db.query(TacticalDispatchPlan)
    if detection_id is not None:
        query = query.filter(TacticalDispatchPlan.fire_detection_id == detection_id)

    plans = query.order_by(TacticalDispatchPlan.created_at.desc()).limit(limit).all()

    results = []
    for p in plans:
        results.append({
            "id": p.id,
            "fire_detection_id": p.fire_detection_id,
            "incident_caption": p.incident_caption,
            "available_forces": p.available_forces,
            "tactical_order": p.tactical_order,
            "created_at": p.created_at.isoformat() if p.created_at else None
        })
    return results


@router.get("/{plan_id}")
def get_dispatch_plan_by_id(plan_id: int, db: Session = Depends(get_db)):
    plan = db.query(TacticalDispatchPlan).filter(TacticalDispatchPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Sevk planı bulunamadı.")

    return {
        "id": plan.id,
        "fire_detection_id": plan.fire_detection_id,
        "incident_caption": plan.incident_caption,
        "available_forces": plan.available_forces,
        "tactical_order": plan.tactical_order,
        "created_at": plan.created_at.isoformat() if plan.created_at else None
    }


@router.get("/by-detection/{detection_id}")
def get_dispatches_by_detection(detection_id: int, db: Session = Depends(get_db)):
    plans = (
        db.query(TacticalDispatchPlan)
        .filter(TacticalDispatchPlan.fire_detection_id == detection_id)
        .order_by(TacticalDispatchPlan.created_at.desc())
        .all()
    )
    
    return [
        {
            "id": p.id,
            "fire_detection_id": p.fire_detection_id,
            "incident_caption": p.incident_caption,
            "available_forces": p.available_forces,
            "tactical_order": p.tactical_order,
            "created_at": p.created_at.isoformat() if p.created_at else None
        }
        for p in plans
    ]