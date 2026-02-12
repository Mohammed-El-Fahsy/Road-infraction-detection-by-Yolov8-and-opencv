from controller import Robot
import cv2
import numpy as np
import os
from ultralytics import YOLO

# ==========================
# INITIALISATION ROBOT
# ==========================
robot = Robot()
TIME_STEP = int(robot.getBasicTimeStep())

camera = robot.getDevice("camera")
camera.enable(TIME_STEP)

width = camera.getWidth()
height = camera.getHeight()

# ==========================
# PARAMÈTRES
# ==========================
INTERDIT_LINE_Y = int(height * 0.55)
VIOLATION_DELAY = 0.03   # 0.3 seconde

images_dir = "/media/ubuntu/data/interdit_violations"
os.makedirs(images_dir, exist_ok=True)

# Charger YOLOv8
model = YOLO("yolov8s.pt")   # plus stable que yolov8n

tracked_cars = {}
violation_timers = {}

# ==========================
# TRACKING SIMPLE
# ==========================
def track_car(box):
    x, y, w, h = box
    center = (x + w//2, y + h//2)

    for car_id, data in tracked_cars.items():
        lx, ly, lw, lh = data['box']
        last_center = (lx + lw//2, ly + lh//2)

        dist = np.sqrt((center[0]-last_center[0])**2 +
                       (center[1]-last_center[1])**2)

        if dist < 60:
            return car_id

    return len(tracked_cars)

# ==========================
# BOUCLE PRINCIPALE
# ==========================
print("=== YOLO INTERDIT DETECTION ===")

while robot.step(TIME_STEP) != -1:

    img = camera.getImage()
    if img is None:
        continue

    frame = np.frombuffer(img, np.uint8).reshape((height, width, 4))
    frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
    display = frame.copy()

    current_time = robot.getTime()

    # ROI (bas image seulement)
    roi_y = int(height * 0.3)
    roi = frame[roi_y:height, :]

    # YOLO detection
    results = model(roi, verbose=False)

    # Dessiner ligne rouge
    cv2.line(display, (0, INTERDIT_LINE_Y),
             (width, INTERDIT_LINE_Y),
             (0,0,255), 3)

    detected_ids = []

    for r in results:
        for box in r.boxes:

            cls = int(box.cls[0])
            conf = float(box.conf[0])

            # Classe voiture = 2 (COCO)
            if cls == 2 and conf > 0.3:

                x1, y1, x2, y2 = map(int, box.xyxy[0])

                # Ajuster coordonnées ROI
                y1 += roi_y
                y2 += roi_y

                w = x2 - x1
                h = y2 - y1

                car_box = (x1, y1, w, h)

                car_id = track_car(car_box)
                tracked_cars[car_id] = {
                    'box': car_box,
                    'last_seen': current_time
                }

                detected_ids.append(car_id)

                # Dessiner bounding box
                cv2.rectangle(display, (x1,y1), (x2,y2),
                              (255,0,0), 2)

                cv2.putText(display, f"CAR_{car_id}",
                            (x1, y1-10),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.6, (0,255,0), 2)

                # ==========================
                # CONTACT LIGNE ROUGE
                # ==========================
                touching_line = (y1 < INTERDIT_LINE_Y < y2)

                if touching_line:

                    if car_id not in violation_timers:
                        violation_timers[car_id] = {
                            "start_time": current_time,
                            "captured": False
                        }

                    duration = current_time - violation_timers[car_id]["start_time"]

                    cv2.putText(display, f"Timer: {duration:.2f}s",
                                (x1, y1-30),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                0.6, (0,255,255), 2)

                    if duration >= VIOLATION_DELAY and not violation_timers[car_id]["captured"]:

                        img_name = f"interdit_{int(current_time*1000)}_CAR_{car_id}.png"
                        img_path = os.path.join(images_dir, img_name)

                        cv2.imwrite(img_path, display)

                        violation_timers[car_id]["captured"] = True
                        print(f"[CAPTURE] CAR_{car_id}")

                else:
                    # Reset timer si plus en contact
                    if car_id in violation_timers:
                        del violation_timers[car_id]

    # Nettoyage voitures disparues
    for car_id in list(tracked_cars.keys()):
        if current_time - tracked_cars[car_id]['last_seen'] > 2:
            if car_id in violation_timers:
                del violation_timers[car_id]
            del tracked_cars[car_id]

    cv2.imshow("YOLO Interdit Monitoring", display)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
