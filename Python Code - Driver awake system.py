import cv2 import numpy as np import dlib  
from imutils import face_utils import serial import time import pygame  
  
# --------- Pygame setup for alert sound --------- pygame.mixer.init()  alert_sound = pygame.mixer.Sound("alert.wav")  # Ensure the file is in the same folder  
  
# --------- Connect to Arduino --------- try:     arduino = serial.Serial('COM3', 9600, timeout=1)     time.sleep(2)  # Give time to Arduino to reset except:  
    print("⚠️ Could not connect to Arduino on COM3.")     arduino = None  
  
# --------- Camera setup --------- cap = cv2.VideoCapture(0) if not cap.isOpened():  
    print("❌ Error: Could not open webcam.")     exit()  
  
# --------- Load dlib's models --------- detector 
= dlib.get_frontal_face_detector()  
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")   
# --------- Eye aspect ratio calculation --------- def euclidean(ptA, ptB):     return np.linalg.norm(ptA - ptB)   def eye_aspect_ratio(eye_points):  
    A = euclidean(eye_points[1], eye_points[5])  
    B = euclidean(eye_points[2], eye_points[4])     C = euclidean(eye_points[0], eye_points[3])      ear = (A + B) / (2.0 * C)     return ear  
  
# --------- Thresholds and counters ---------  
SLEEP_THRESH = 0.21 DROWSY_THRESH = 0.25 
sleep_counter = 0 drowsy_counter 
= 0 active_counter = 0  
  
sleep_limit = 60  # ~3 seconds at 20 FPS drowsy_limit = 30  # ~1.5 seconds active_limit = 15  
  
status = "" color = (0, 255, 0) sleep_alert_played 
= False drowsy_alert_played 
= False  
  
# --------- Main loop --------- while True:     ret, frame = cap.read()     if not ret:         print("⚠️ Frame read failed.")         continue  
  
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)      faces = detector(gray)  
     for face in faces:         shape 
= predictor(gray, face)  
        shape_np = face_utils.shape_to_np(shape)  
  
        left_eye = shape_np[36:42]         right_eye = shape_np[42:48]         left_ear = eye_aspect_ratio(left_eye)         right_ear = eye_aspect_ratio(right_eye)         ear = 
(left_ear + right_ear) / 2.0           if ear < SLEEP_THRESH:             sleep_counter += 1             drowsy_counter = 0             active_counter = 0             if sleep_counter > sleep_limit:                  status = "SLEEPING !!!"  
                color = (0, 0, 255)                 if not sleep_alert_played:                     if arduino:                         
arduino.write(b'a')                     alert_sound.play()                     sleep_alert_played = True                     drowsy_alert_played = False         elif ear < 
DROWSY_THRESH:             drowsy_counter += 1             sleep_counter = 0             active_counter = 
0             if drowsy_counter > drowsy_limit:                 status = "Drowsy !"                 color = (0, 
0, 255)                 if not 
drowsy_alert_played:                     if arduino:                         arduino.write(b'a')                     alert_sound.play()                     drowsy_alert_played = True                     sleep_alert_played = False         else:             
active_counter += 1             sleep_counter = 0             drowsy_counter = 0             if active_counter > active_limit:                 status = "Active :)"                 color = 
(0, 255, 0)                 if arduino:                     arduino.write(b'b')                 sleep_alert_played = False                 drowsy_alert_played = False  
  
        # Draw status and landmarks          cv2.putText(frame, status, (100, 100), cv2.FONT_HERSHEY_SIMPLEX,  
1.2, color, 3)         for (x, y) in shape_np:             
cv2.circle(frame, (x, y), 1, (255, 255, 255), -1)  
  
    cv2.imshow("Driver Drowsiness Detection", frame)     if cv2.waitKey(1) == 27:  # ESC key         break  
  
cap.release() cv2.destroyAllWindows()  
  
