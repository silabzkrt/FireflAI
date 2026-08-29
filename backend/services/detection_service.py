"""
FireflAI - Drone Vision YOLO Detection Service

Wraps Ultralytics YOLO inference for aerial wildfire surveillance.
Supports single-frame image analysis and multi-frame video stream decoding, identifying
smoke and fire classes with bounding boxes and confidence scores.
"""

import os
import cv2
import tempfile
import numpy as np
from ultralytics import YOLO

script_dir = os.path.dirname(os.path.abspath(__file__))
yolo_path = os.path.join(script_dir, "..", "models", "detection_model", "detection_model.pt")

class YoloDetectionService:
    def __init__(self):
        try:
            self.model = YOLO(yolo_path)
            print("YOLO Model loaded successfully.")
        except Exception as e:
            print(f"Failed to load YOLO Model: {e}")
            self.model = None

    def run_inference(self, image_bytes: bytes, conf_threshold: float = 0.25):
        if not self.model:
            return {"detected": False, "results": []}

        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if img is None:
            return {"detected": False, "results": [], "error": "Invalid image format"}

        results = self.model(img, conf=conf_threshold)[0]
        detections = []

        for box in results.boxes:
            class_id = int(box.cls[0])
            class_name = self.model.names[class_id]
            confidence = float(box.conf[0])
            xyxy = box.xyxy[0].tolist()

            detections.append({
                "class_name": class_name,
                "confidence": round(confidence, 4),
                "bbox": xyxy
            })

        return {
            "detected": len(detections) > 0,
            "results": detections
        }

    def run_video_inference(self, video_bytes: bytes, conf_threshold: float = 0.25):
        if not self.model:
            return {"detected": False, "results": []}

        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp_file:
            tmp_file.write(video_bytes)
            tmp_video_path = tmp_file.name

        cap = cv2.VideoCapture(tmp_video_path)
        
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_stride = int(fps) if (fps and fps > 0) else 30

        all_detections = []
        frame_count = 0
        detected_any = False

        try:
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break

                if frame_count % frame_stride == 0:
                    results = self.model(frame, conf=conf_threshold)[0]
                    frame_detections = []

                    for box in results.boxes:
                        class_id = int(box.cls[0])
                        class_name = self.model.names[class_id]
                        confidence = float(box.conf[0])
                        xyxy = box.xyxy[0].tolist()

                        frame_detections.append({
                            "class_name": class_name,
                            "confidence": round(confidence, 4),
                            "bbox": xyxy
                        })

                    if frame_detections:
                        detected_any = True
                        all_detections.append({
                            "frame_index": frame_count,
                            "timestamp_sec": round(frame_count / frame_stride, 2),
                            "detections": frame_detections
                        })

                frame_count += 1
        finally:
            cap.release()
            if os.path.exists(tmp_video_path):
                os.remove(tmp_video_path)

        return {
            "detected": detected_any,
            "total_frames_processed": frame_count,
            "detections_by_frame": all_detections
        }