from ultralytics import YOLO
import cv2

# Charger le modèle
model = YOLO("yolov8s.pt")

# Ouvrir la webcam (0 = webcam par défaut)
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Détection
    results = model(frame)

    # Affichage des résultats
    annotated_frame = results[0].plot()

    cv2.imshow("Detection Fruits & Legumes", annotated_frame)

    # Quitter avec touche Q
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()