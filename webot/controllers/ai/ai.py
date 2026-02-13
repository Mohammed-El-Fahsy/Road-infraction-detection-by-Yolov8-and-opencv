from controller import Robot
import cv2
import numpy as np
import pytesseract
import os

# ==========================
# INITIALISATION ROBOT
# ==========================
robot = Robot()
TIME_STEP = int(robot.getBasicTimeStep())

camera = robot.getDevice("camera")
camera.enable(TIME_STEP)
width = camera.getWidth()
height = camera.getHeight()

# ROI dynamiques
FEU_Y2 = int(height * 0.25)
ROUTE_Y1 = int(height * 0.35)
VIOLATION_LINE_Y = int(height * 0.55)

# Paramètre de délai de violation (1 seconde)
VIOLATION_DELAY = 0.4 

# OCR
pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"

# Dossier pour stocker les images dans la partition data
images_dir = "/media/ubuntu/data/violations_images"
os.makedirs(images_dir, exist_ok=True)

# ==========================
# FONCTIONS
# ==========================
def read_plate(img):
    """OCR pour plaque"""
    if img is None or img.size == 0:
        return ""
    
    scale_factor = 2
    h, w = img.shape[:2]
    resized = cv2.resize(img, (w * scale_factor, h * scale_factor), interpolation=cv2.INTER_CUBIC)
    
    gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
    gray = cv2.equalizeHist(gray)
    gray = cv2.bilateralFilter(gray, 11, 75, 75)
    
    thresh = cv2.adaptiveThreshold(gray, 255, 
                                   cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                   cv2.THRESH_BINARY, 11, 2)
    
    custom_config = r'--oem 3 --psm 8 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    text = pytesseract.image_to_string(thresh, config=custom_config)
    
    text = ''.join(c for c in text if c.isalnum())
    return text

def detect_red_light(frame):
    roi = frame[0:FEU_Y2, int(width*0.25):int(width*0.75)]
    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    lower1 = np.array([0,100,100])
    upper1 = np.array([10,255,255])
    lower2 = np.array([160,100,100])
    upper2 = np.array([180,255,255])
    mask = cv2.inRange(hsv, lower1, upper1) + cv2.inRange(hsv, lower2, upper2)
    return cv2.countNonZero(mask) > 30

def detect_car(frame):
    roi = frame[ROUTE_Y1:height, :]
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)
    kernel = np.ones((5,5), np.uint8)
    edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for c in contours:
        area = cv2.contourArea(c)
        if 3000 < area < 60000:
            x, y, w, h = cv2.boundingRect(c)
            ratio = w/h if h > 0 else 0
            if 1.2 < ratio < 3.5:
                return True, (x, y+ROUTE_Y1, w, h)
    return False, None

def track_car_by_position(car_box, tracked_cars):
    x, y, w, h = car_box
    car_center = (x + w//2, y + h//2)
    
    for car_id, car_data in tracked_cars.items():
        last_box = car_data['last_box']
        last_center = (last_box[0] + last_box[2]//2, last_box[1] + last_box[3]//2)
        
        distance = np.sqrt((car_center[0] - last_center[0])**2 + 
                          (car_center[1] - last_center[1])**2)
        
        if distance < 50:
            return car_id
    
    new_id = len(tracked_cars)
    return new_id

# ==========================
# BOUCLE PRINCIPALE
# ==========================
frame_count = 0
print("=== CONTROLEUR PYTHON DEMARRE ===")
print(f"Délai de violation: {VIOLATION_DELAY} seconde(s)")

tracked_cars = {}
last_plate_text = ""
plate_stability_counter = 0
stable_plate_text = ""
violation_timers = {}

while robot.step(TIME_STEP) != -1:
    img = camera.getImage()
    if img is None:
        continue

    frame = np.frombuffer(img, np.uint8).reshape((height, width, 4))
    frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

    red = detect_red_light(frame)
    car, box = detect_car(frame)
    display = frame.copy()
    current_time = robot.getTime()

    # ROI Debug
    cv2.line(display, (0, FEU_Y2), (width, FEU_Y2), (255,0,0), 2)
    cv2.line(display, (0, ROUTE_Y1), (width, ROUTE_Y1), (0,255,0), 2)
    cv2.line(display, (0, VIOLATION_LINE_Y), (width, VIOLATION_LINE_Y), (0,255,255), 2)

    if car:
        x, y, w, h = box
        cv2.rectangle(display, (x,y), (x+w,y+h), (255,0,0), 2)
        cv2.putText(display,"CAR",(x,y-10),cv2.FONT_HERSHEY_SIMPLEX,0.7,(255,0,0),2)

        # Tracking
        car_id = track_car_by_position(box, tracked_cars)
        tracked_cars[car_id] = {
            'last_box': box,
            'last_seen': current_time
        }
        
        # Lecture de plaque
        if frame_count % 5 == 0:
            plaque_y1 = max(y + int(h*0.75), 0)
            plaque_y2 = min(y + h, height)
            plaque_x1 = max(x, 0)
            plaque_x2 = min(x + w, width)
            
            plate_roi = frame[plaque_y1:plaque_y2, plaque_x1:plaque_x2]
            
            if plate_roi.shape[0] > 20 and plate_roi.shape[1] > 60:
                current_plate_text = read_plate(plate_roi)
                
                if current_plate_text == last_plate_text:
                    plate_stability_counter += 1
                    if plate_stability_counter >= 3 and len(current_plate_text) >= 2:
                        stable_plate_text = current_plate_text
                        tracked_cars[car_id]['plate_text'] = stable_plate_text
                else:
                    plate_stability_counter = 0
                
                last_plate_text = current_plate_text
                
                if stable_plate_text:
                    cv2.putText(display, f"Plate: {stable_plate_text}", 
                               (x, y-50), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        # DETECTION VIOLATION
        if red and y+h > VIOLATION_LINE_Y:
            if 'plate_text' in tracked_cars[car_id] and tracked_cars[car_id]['plate_text']:
                plate_text = tracked_cars[car_id]['plate_text']
            else:
                plate_text = f"CAR_{car_id}"
            
            if plate_text not in violation_timers:
                violation_timers[plate_text] = {
                    'start_time': current_time,
                    'captured': False,
                    'car_id': car_id
                }
                print(f"[TIMER START] {plate_text} - Timer started at {current_time:.2f}s")
            
            violation_duration = current_time - violation_timers[plate_text]['start_time']
            
            # Affichage du compteur
            timer_text = f"Viol: {violation_duration:.1f}s"
            cv2.putText(display, timer_text, (x, y-30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
            
            # Sauvegarde image après délai
            if violation_duration >= VIOLATION_DELAY and not violation_timers[plate_text]['captured']:
                img_name = f"violation_{int(current_time*1000)}_{plate_text}.png"
                img_path = os.path.join(images_dir, img_name)
                cv2.imwrite(img_path, display)
                violation_timers[plate_text]['captured'] = True
                print(f"[VIOLATION CAPTURED] {plate_text} -> {img_name}")
        
        else:
            # Reset timer si feu vert
            for plate in list(violation_timers.keys()):
                if violation_timers[plate]['car_id'] == car_id:
                    del violation_timers[plate]
                    break

    # Nettoyage voitures disparues
    cars_to_remove = []
    for car_id, car_data in list(tracked_cars.items()):
        if current_time - car_data['last_seen'] > 2.0:
            cars_to_remove.append(car_id)
    for car_id in cars_to_remove:
        for plate in list(violation_timers.keys()):
            if violation_timers[plate]['car_id'] == car_id:
                del violation_timers[plate]
                break
        del tracked_cars[car_id]

    # Info feu
    if red:
        cv2.putText(display,"RED LIGHT",(20,40),cv2.FONT_HERSHEY_SIMPLEX,1,(0,0,255),3)
    else:
        cv2.putText(display,"GREEN",(20,40),cv2.FONT_HERSHEY_SIMPLEX,1,(0,255,0),3)

    # Affichage
    frame_count += 1
    if frame_count % 3 == 0:
        cv2.imshow("Traffic Monitoring", display)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cv2.destroyAllWindows()
