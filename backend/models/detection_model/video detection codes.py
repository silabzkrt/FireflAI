import cv2
from ultralytics import YOLO

model = YOLO("detection_model.pt")

#code for watching the the video with detections
cap = cv2.VideoCapture("1.mp4")

print("Starting To Detect")

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        print("Done.")
        break

    results = model(frame, conf=0.45) #confidence score
    
    annotated_frame = results[0].plot()
    
    cv2.imshow("Drone / Optic Viewing", annotated_frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

#code for watching and saving the video with detections
model.predict(source="3.mp4", save=True, conf=0.45, show=True)