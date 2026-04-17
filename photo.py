import cv2
import os

# =============================
# CONFIGURATION
# =============================

classes = ["banane", "carotte", "champignon", "citron", "clementine", "fraise", "mais", "poire", "poivron", "radis", "tomate", "tomate_cerise"]
dataset_type = "train"  # "train" ou "val"
base_path = f"dataset-2/{dataset_type}"

# =============================
# CREATION DOSSIERS SI NECESSAIRE
# =============================

for cls in classes:
    os.makedirs(os.path.join(base_path, cls), exist_ok=True)

# =============================
# WEBCAM
# =============================

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Erreur ouverture webcam")
    exit()

current_class_index = 0
image_count = 0

print("=== APPLICATION CAPTURE DATASET ===")
print("Touches :")
print("  n  -> classe suivante")
print("  p  -> classe précédente")
print("  s  -> sauvegarder image")
print("  q  -> quitter")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    current_class = classes[current_class_index]

    # Affichage infos
    """text = f"Classe: {current_class}"
    cv2.putText(frame, text, (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                1, (0, 255, 0), 2)"""

    cv2.imshow("Capture Dataset", frame)

    key = cv2.waitKey(1) & 0xFF

    # Quitter
    if key == ord("q"):
        break

    # Classe suivante
    if key == ord("n"):
        current_class_index = (current_class_index + 1) % len(classes)
        image_count = 0

    # Classe précédente
    if key == ord("p"):
        current_class_index = (current_class_index - 1) % len(classes)
        image_count = 0

    # Sauvegarder image
    if key == ord("s"):
        save_path = os.path.join(
            base_path,
            current_class,
            f"{current_class}_{image_count}.jpg"
        )
        cv2.imwrite(save_path, frame)
        print(f"Image sauvegardée: {save_path}")
        image_count += 1

cap.release()
cv2.destroyAllWindows()