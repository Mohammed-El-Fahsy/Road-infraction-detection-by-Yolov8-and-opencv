from controller import Robot
import cv2
import numpy as np
import os
from ultralytics import YOLO
robot = Robot()
TIME_STEP = int(robot.getBasicTimeStep())

camera = robot.getDevice("camera")
camera.enable(TIME_STEP)

width = camera.getWidth()
height = camera.getHeight()

ANGLE_DEG = 75        
VIOLATION_DELAY = 0.1   

images_dir = "/media/ubuntu/data/ligne_violations"
os.makedirs(images_dir, exist_ok=True)

model = YOLO("yolov8s.pt")

tracked_cars = {}
violation_timers = {}

LINE_CENTER_X = width // 2
LINE_CENTER_Y = height // 2
LINE_LENGTH = max(width, height)

angle_rad = np.deg2rad(ANGLE_DEG)

dx = int(np.cos(angle_rad) * LINE_LENGTH)
dy = int(np.sin(angle_rad) * LINE_LENGTH)

x1_line = LINE_CENTER_X - dx
y1_line = LINE_CENTER_Y - dy
x2_line = LINE_CENTER_X + dx
y2_line = LINE_CENTER_Y + dy

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

print("=== YOLO LIGNE CONTINUE INCLINÉE ===")

while robot.step(TIME_STEP) != -1:

    img = camera.getImage()
    if img is None:
        continue

    frame = np.frombuffer(img, np.uint8).reshape((height, width, 4))
    frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
    display = frame.copy()

    current_time = robot.getTime()

    roi_y = int(height * 0.3)
    roi = frame[roi_y:height, :]

    results = model(roi, verbose=False)

    cv2.line(display,
             (x1_line, y1_line),
             (x2_line, y2_line),
             (0,0,255), 3)

    detected_ids = []

    for r in results:
        for box in r.boxes:

            cls = int(box.cls[0])
            conf = float(box.conf[0])

            if cls == 2 and conf > 0.4:

                x1, y1, x2, y2 = map(int, box.xyxy[0])

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

                cv2.rectangle(display, (x1,y1), (x2,y2),
                              (255,0,0), 2)

                cv2.putText(display, f"CAR_{car_id}",
                            (x1, y1-10),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.6, (0,255,0), 2)
                            
                cx = x1 + w//2
                cy = y1 + h//2

                num = abs((y2_line - y1_line)*cx -
                          (x2_line - x1_line)*cy +
                          x2_line*y1_line -
                          y2_line*x1_line)

                den = np.sqrt((y2_line - y1_line)**2 +
                              (x2_line - x1_line)**2)

                distance = num / den if den != 0 else 999

                touching_line = distance < 65

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

                        img_name = f"violation_{int(current_time*1000)}_CAR_{car_id}.png"
                        img_path = os.path.join(images_dir, img_name)

                        cv2.imwrite(img_path, display)

                        violation_timers[car_id]["captured"] = True
                        print(f"[CAPTURE] CAR_{car_id}")

                else:
                    if car_id in violation_timers:
                        del violation_timers[car_id]


    for car_id in list(tracked_cars.keys()):
        if current_time - tracked_cars[car_id]['last_seen'] > 2:
            if car_id in violation_timers:
                del violation_timers[car_id]
            del tracked_cars[car_id]

    cv2.imshow("Ligne Continue Detection", display)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
