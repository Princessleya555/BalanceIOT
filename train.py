from ultralytics import YOLO

# Charger modèle classification pré-entraîné
model = YOLO("yolov8n-cls.pt")

# Entraîner sur ton dataset
model.train(
    data="dataset-2",
    epochs=30,
    imgsz=224,
    batch=16
)