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
    detection = db.query(FireDetection).filter(FireDetection.id == payload.detection_id).first()
    if not detection:
        raise HTTPException(status_code=404, detail=f"Detection ID {payload.detection_id} bulunamadı.")

    try:
        plan_data = dispatch_service.generate_dispatch_plan(
            detection_id=payload.detection_id,
            class_name=detection.class_name,
            confidence=detection.confidence
        )

        new_plan = TacticalDispatchPlan(
            fire_detection_id=payload.detection_id,
            incident_caption=plan_data.get("action_summary", "Müdahale Planı"),
            available_forces=str(plan_data.get("assigned_resources", {})),
            tactical_order=plan_data.get("action_summary", "")
        )
        db.add(new_plan)
        db.commit()

        return plan_data

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
    """Geçmişteki N adet sevk planını getirir (Opsiyonel olarak detection_id ile filtrelenebilir)."""
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
    """Spesifik bir sevk planını kendi plan ID'si ile getirir."""
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
    """Belirli bir yangın tespitine ait tüm sevk/müdahale planlarını getirir."""
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