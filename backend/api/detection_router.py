"""
FireflAI - Drone Vision & Fire Detection API Router

Provides HTTP endpoints and WebSocket streams for real-time aerial fire detection.
Accepts drone camera video/image feeds, performs YOLO inference, stores detection events
in the database, and broadcasts emergency alerts to connected clients.
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends, WebSocket, WebSocketDisconnect
from typing import List
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from services.detection_service import YoloDetectionService
from database.session import get_db
from database.models import FireDetection

router = APIRouter()
yolo_service = YoloDetectionService()

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            await connection.send_json(message)

manager = ConnectionManager()

@router.websocket("/ws/live-alerts")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@router.post("/detect-frame")
async def detect_frame(
    file: UploadFile = File(...),
    latitude: float = Form(...),
    longitude: float = Form(...),
    db = Depends(get_db)
):
    try:
        contents = await file.read()
        
        if file.content_type and "video" in file.content_type or file.filename.endswith(('.mp4', '.avi', '.mov', '.mkv')):
            detection_result = yolo_service.run_video_inference(contents)
        else:
            detection_result = yolo_service.run_inference(contents)

        saved_records_count = 0

        if detection_result["detected"]:
            if "detections_by_frame" in detection_result:
                for frame_data in detection_result["detections_by_frame"]:
                    for det in frame_data["detections"]:
                        new_record = FireDetection(
                            class_name=det.get("class_name", "wildfire"),
                            confidence=det.get("confidence", 0.0),
                            detection_point=f"POINT({longitude} {latitude})"
                        )
                        db.add(new_record)
                        saved_records_count += 1
                db.commit()

                await manager.broadcast({
                    "event": "FIRE_DETECTED_IN_VIDEO",
                    "total_detections_saved": saved_records_count,
                    "latitude": latitude,
                    "longitude": longitude,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })

            else:
                for det in detection_result.get("results", []):
                    new_record = FireDetection(
                        class_name=det.get("class_name", "wildfire"),
                        confidence=det.get("confidence", 0.0),
                        detection_point=f"POINT({longitude} {latitude})"
                    )
                    db.add(new_record)
                    saved_records_count += 1
                db.commit()

        detection_result["saved_to_db_count"] = saved_records_count
        return detection_result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Detection failed: {str(e)}")

@router.get("/history")
def get_detection_history(limit: int = 50, db: Session = Depends(get_db)):
    detections = (
        db.query(FireDetection)
        .order_by(FireDetection.captured_at.desc())
        .limit(limit)
        .all()
    )
    
    results = []
    for d in detections:
        results.append({
            "id": d.id,
            "class_name": d.class_name,
            "confidence": d.confidence,
            "latitude": d.latitude,
            "longitude": d.longitude,
            "detection_point": d.detection_point,
            "captured_at": d.captured_at.isoformat() if d.captured_at else None
        })
    return results

@router.get("/{detection_id}")
def get_detection_by_id(detection_id: int, db: Session = Depends(get_db)):
    detection = db.query(FireDetection).filter(FireDetection.id == detection_id).first()
    if not detection:
        raise HTTPException(status_code=404, detail="Yangın tespiti bulunamadı.")
    
    return {
        "id": detection.id,
        "class_name": detection.class_name,
        "confidence": detection.confidence,
        "latitude": detection.latitude,
        "longitude": detection.longitude,
        "detection_point": detection.detection_point,
        "captured_at": detection.captured_at.isoformat() if detection.captured_at else None
    }