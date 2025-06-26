import math
import time

import cv2
import mediapipe as mp

# Inizializzazione MediaPipe
mp_pose = mp.solutions.pose
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

# Impostazioni
pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
hands = mp_hands.Hands(
    max_num_hands=2,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

# Apri webcam
cap = cv2.VideoCapture(0)

time_tick = time.time_ns()
while cap.isOpened():
    success, frame = cap.read()
    if not success:
        print("Errore nella lettura del frame.")
        break

    # Flip orizzontale e conversione a RGB
    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Disattiva scrittura su immagine
    rgb_frame.flags.writeable = False

    # Rilevamento corpo e mani
    pose_results = pose.process(rgb_frame)
    hands_results = hands.process(rgb_frame)

    # Riattiva scrittura su immagine
    rgb_frame.flags.writeable = True

    shoulder = None
    # Disegna risultati sul frame originale
    if pose_results.pose_landmarks:
        mp_drawing.draw_landmarks(
            frame, pose_results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
            mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
            mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2)
        )
        shoulder = pose_results.pose_landmarks.landmark[mp.solutions.pose.PoseLandmark.LEFT_SHOULDER]

    index_tip = None
    min_dist = None
    if hands_results.multi_hand_landmarks:
        min_dist = 0
        for hand_landmarks in hands_results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(
                frame, hand_landmarks, mp_hands.HAND_CONNECTIONS,
                mp_drawing.DrawingSpec(color=(121, 22, 76), thickness=2, circle_radius=2),
                mp_drawing.DrawingSpec(color=(250, 44, 250), thickness=2)
            )
            min_dist = max(min_dist, math.sqrt((hand_landmarks.landmark[4].x - hand_landmarks.landmark[6].x) ** 2 +
                           (hand_landmarks.landmark[4].y - hand_landmarks.landmark[6].y) ** 2 +
                           (hand_landmarks.landmark[4].z - hand_landmarks.landmark[6].z) ** 2))

    if min_dist is not None and time.time_ns() - time_tick > 2e9:
        print("Max dist: \n", min_dist)
        time_tick = time.time_ns()
    # Mostra il frame
    cv2.imshow('MediaPipe Body and Hands', frame)

    # Esci con 'q'
    if cv2.waitKey(5) & 0xFF == ord('q'):
        break

# Rilascia risorse
cap.release()
cv2.destroyAllWindows()
pose.close()
hands.close()
