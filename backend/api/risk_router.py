from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone

from database.session import get_db
from database.models import MeteorologicalRisk
from schemas.risk_schema import SinglePointRiskRequest, RiskReportResponse
from services.risk_service import RiskPredictionService
from core import constants

router = APIRouter()
risk_service = RiskPredictionService()

@router.post("/predict-point", response_model=RiskReportResponse)
async def predict_single_point_risk(
    payload: SinglePointRiskRequest, 
    db: Session = Depends(get_db)
):
    try:
        hours_ago = payload.hours_ago or 0
        target_time = datetime.now(timezone.utc) - timedelta(hours=hours_ago)
        loc_name = payload.location_name or "Unknown Location"
        
        time_window_start = target_time - timedelta(minutes=30)
        time_window_end = target_time + timedelta(minutes=30)

        existing_record = db.query(MeteorologicalRisk).filter(
            MeteorologicalRisk.captured_at >= time_window_start,
            MeteorologicalRisk.captured_at <= time_window_end,
            MeteorologicalRisk.latitude.between(payload.latitude - 0.05, payload.latitude + 0.05),
            MeteorologicalRisk.longitude.between(payload.longitude - 0.05, payload.longitude + 0.05)
        ).first()

        if existing_record:
            return {
                "location_name": f"{loc_name} (Cached)",
                "latitude": payload.latitude,
                "longitude": payload.longitude,
                "risk_score": existing_record.risk_level,
                "temperature": existing_record.temperature,
                "humidity": existing_record.humidity,
                "rh": existing_record.humidity,
                "wind_speed": existing_record.wind_speed,
                "wind_direction": existing_record.wind_direction,
                "status": "cached",
                "captured_at": existing_record.captured_at.isoformat() if existing_record.captured_at else None
            }

        report = risk_service.analyze_single_location(
            location_name=loc_name,
            lat=payload.latitude,
            lon=payload.longitude,
            hours_ago=hours_ago
        )
        
        risk_score = report.get("risk_score", 0.0)
        temp = report.get("temperature")
        rh = report.get("humidity") or report.get("rh")
        ws = report.get("wind_speed")
        wdir = report.get("wind_direction")

        new_risk_record = MeteorologicalRisk(
            risk_level=float(risk_score),
            latitude=float(payload.latitude),
            longitude=float(payload.longitude),
            temperature=float(temp) if temp is not None else None,
            humidity=float(rh) if rh is not None else None,
            wind_speed=float(ws) if ws is not None else None,
            wind_direction=float(wdir) if wdir is not None else None,
            risk_point=f"POINT({payload.longitude} {payload.latitude})",
            captured_at=target_time
        )
        db.add(new_risk_record)
        db.commit()

        report["captured_at"] = target_time.isoformat()
        return report

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Risk prediction failed: {str(e)}")

@router.get("/turkey-grid")
async def get_turkey_grid_risk(
    hours_ago: int = Query(0, ge=0, le=168, description="0 = Current, >0 = Past hours ago"),
    db: Session = Depends(get_db)
):
    try:
        from main import RISK_CACHE
        
        if hours_ago == 0 and hours_ago in RISK_CACHE and RISK_CACHE[hours_ago]:
            return {
                "hours_ago": hours_ago,
                "total_points": len(RISK_CACHE[hours_ago]),
                "data": RISK_CACHE[hours_ago]
            }
        
        target_time = datetime.now(timezone.utc) - timedelta(hours=hours_ago)
        time_window_start = target_time - timedelta(minutes=30)
        time_window_end = target_time + timedelta(minutes=30)

        records = db.query(MeteorologicalRisk).filter(
            MeteorologicalRisk.captured_at >= time_window_start,
            MeteorologicalRisk.captured_at <= time_window_end
        ).all()

        if not records:
            calculated_points = risk_service.get_turkey_grid_risk(
                threshold=constants.DEFAULT_GRID_RISK_THRESHOLD,
                hours_ago=hours_ago
            )
            
            if calculated_points:
                new_records = []
                for p in calculated_points:
                    lat = p.get("latitude")
                    lon = p.get("longitude")
                    score = p.get("risk_score", 0.0)
                    temp = p.get("temperature")
                    rh = p.get("humidity")
                    ws = p.get("wind_speed")
                    wdir = p.get("wind_direction")

                    if lat is not None and lon is not None:
                        record = MeteorologicalRisk(
                            risk_level=float(score),
                            latitude=float(lat),
                            longitude=float(lon),
                            temperature=float(temp) if temp is not None else None,
                            humidity=float(rh) if rh is not None else None,
                            wind_speed=float(ws) if ws is not None else None,
                            wind_direction=float(wdir) if wdir is not None else None,
                            risk_point=f"POINT({lon} {lat})",
                            captured_at=target_time
                        )
                        new_records.append(record)
                
                db.bulk_save_objects(new_records)
                db.commit()

                records = db.query(MeteorologicalRisk).filter(
                    MeteorologicalRisk.captured_at >= time_window_start,
                    MeteorologicalRisk.captured_at <= time_window_end
                ).all()

        fixed_locs = getattr(constants, "FIXED_LOCATIONS", [])
        formatted_data = []

        for r in records:
            lat_val = float(r.latitude) if r.latitude is not None else 0.0
            lon_val = float(r.longitude) if r.longitude is not None else 0.0

            matched_fixed_name = None
            for loc in fixed_locs:
                if abs(lat_val - loc[1]) < 0.01 and abs(lon_val - loc[2]) < 0.01:
                    matched_fixed_name = loc[0]
                    break

            display_name = matched_fixed_name if matched_fixed_name else f"Grid ({round(lat_val, 1)}, {round(lon_val, 1)})"

            formatted_data.append({
                "location_name": display_name,
                "latitude": lat_val,
                "longitude": lon_val,
                "risk_score": float(r.risk_level) if r.risk_level is not None else 0.0,
                "temperature": float(r.temperature) if r.temperature is not None else 0.0,
                "humidity": float(r.humidity) if r.humidity is not None else 0.0,
                "wind_speed": float(r.wind_speed) if r.wind_speed is not None else 0.0,
                "wind_direction": float(r.wind_direction) if r.wind_direction is not None else 180.0,
                "is_fixed": bool(matched_fixed_name),
                "captured_at": r.captured_at.isoformat() if r.captured_at else target_time.isoformat()
            })

        return {
            "hours_ago": hours_ago,
            "total_points": len(formatted_data),
            "data": formatted_data
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to fetch Turkey grid risk: {str(e)}")