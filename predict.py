from ultralytics import YOLO
import cv2

model = YOLO("runs/classify/train/weights/best.pt")

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    results = model(frame)

    probs = results[0].probs
    class_id = probs.top1
    confidence = probs.top1conf
    class_name = model.names[class_id]

    text = f"{class_name} ({confidence:.2f})"

    cv2.putText(frame, text, (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                1, (0, 255, 0), 2)

    cv2.imshow("Fruit Classification", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()