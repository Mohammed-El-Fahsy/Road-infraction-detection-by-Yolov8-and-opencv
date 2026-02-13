# Road-infraction-detection-by-Yolov8-and-opencv
This project consists of a real-time road infractions detection system based on computer vision and deep learning. YOLOv8 is used for vehicle detection, while OpenCV is applied for image processing and road line analysis. The system detects traffic violations  by analyzing the position of vehicles relative to road markings.
The first part of the project focuses on control systems. I designed a closed-loop vehicle control system in Webots using a PID controller to ensure accurate line-following behavior. The controller continuously corrects the vehicle’s trajectory based on visual feedback, allowing stable and smooth motion along the lane.

The second part involves computer vision. Using cameras and OpenCV, I implemented real-time line detection and road infraction detection. The system processes video frames to detect continuous line crossings and other lane violations, analyzing the vehicle’s position relative to road markings.

The third component integrates artificial intelligence. I used YOLOv8 for real-time vehicle detection. The detected vehicles are then processed using OpenCV for further analysis and validation of infractions. This combination of deep learning and classical computer vision improves detection robustness and accuracy.

The final part of the project is a web-based infraction management system. I developed a full-stack platform using React and CSS for the frontend, PHP for the backend, and MySQL for the database. The system stores and manages information about each detected infraction, including vehicle data, time, location, and type of violation.

For controllers:
cont: controls the vehicle to follow the yellow line.

white: controls the vehicle to follow the white line.

ai: detects red light violations.

interdet: detects no-entry violations.

ligne: detects solid line violations.
