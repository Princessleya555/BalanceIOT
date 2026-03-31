from ultralytics import YOLO
import cv2

# Charger modèle entraîné
model = YOLO("runs/classify/train/weights/best.pt")

# Charger image
img = cv2.imread("test.jpg")

# Prédiction
results = model(img)

# Récupérer classe prédite
probs = results[0].probs
class_id = probs.top1
confidence = probs.top1conf

class_name = model.names[class_id]

print(f"Fruit détecté : {class_name}")
print(f"Confiance : {confidence:.2f}")