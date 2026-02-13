from controller import Robot, Camera
from vehicle import Driver
import math

# =====================
# PARAMÈTRES
# =====================
TIME_STEP = 50
SPEED = 60.0  # km/h

KP = 0.4
KI = 0.006
KD = 2

UNKNOWN = 99999.0

# Couleur jaune (BGR dans Webots)
YELLOW_REF = (95, 187, 203)
COLOR_THRESHOLD = 30

FILTER_SIZE = 3

# =====================
# INITIALISATION
# =====================
driver = Driver()

camera = driver.getDevice("camera")
camera.enable(TIME_STEP)

width = camera.getWidth()
height = camera.getHeight()
fov = camera.getFov()

driver.setCruisingSpeed(SPEED)
driver.setBrakeIntensity(0.0)

print("=== CONTROLEUR PYTHON DEMARRE ===")

# =====================
# OUTILS
# =====================
def color_diff(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1]) + abs(a[2] - b[2])

def detect_yellow_line(image):
    sum_x = 0
    count = 0

    for y in range(height // 2, height):  # bas de l'image
        for x in range(width):
            index = 4 * (y * width + x)
            b = image[index]
            g = image[index + 1]
            r = image[index + 2]

            if color_diff((b, g, r), YELLOW_REF) < COLOR_THRESHOLD:
                sum_x += x
                count += 1

    if count == 0:
        return UNKNOWN

    mean_x = sum_x / count
    angle = (mean_x / width - 0.5) * fov
    return angle

# =====================
# FILTRE
# =====================
angle_buffer = [0.0] * FILTER_SIZE

def filter_angle(new_angle):
    if new_angle == UNKNOWN:
        return UNKNOWN
    angle_buffer.pop(0)
    angle_buffer.append(new_angle)
    return sum(angle_buffer) / FILTER_SIZE

# =====================
# PID
# =====================
prev_error = 0.0
integral = 0.0

def pid_control(error):
    global prev_error, integral

    if error == UNKNOWN:
        integral = 0.0
        prev_error = 0.0
        return 0.0

    derivative = error - prev_error
    integral += error

    prev_error = error

    return KP * error + KI * integral + KD * derivative

# =====================
# BOUCLE PRINCIPALE
# =====================
while driver.step() != -1:
    image = camera.getImage()
    angle = detect_yellow_line(image)
    angle = filter_angle(angle)

    if angle != UNKNOWN:
        # Ligne détectée → PID pour suivre
        steering = pid_control(angle)
        steering = max(-0.5, min(0.5, steering))
        driver.setSteeringAngle(steering)
        driver.setBrakeIntensity(0.0)
    else:
        # Ligne perdue → avancer tout droit
        driver.setSteeringAngle(0.0)
        driver.setBrakeIntensity(0.0)  # pas de frein
        driver.setCruisingSpeed(SPEED)  # assurer la vitesse
