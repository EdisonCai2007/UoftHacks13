import cv2
import mediapipe as mp
import numpy as np
from collections import deque

mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(refine_landmarks=True)
cap = cv2.VideoCapture(1)

# Increase history to 10 for maximum stability (no flickering)
history_h = deque(maxlen=10)
history_v = deque(maxlen=10)

# --- SETTINGS ---
calibrated = False
center_h, center_v = 0.5, 0.45

# ADJUST THESE TO YOUR LIKING:
# Smaller number = More sensitive (Off screen faster)
# Larger number = Less sensitive (More room to move)
H_THRESHOLD = 0.05
V_THRESHOLD = 0.04

print("Look at the CENTER of your screen and press 'C' to calibrate.")

while cap.isOpened():
    success, image = cap.read()
    if not success: break

    image = cv2.flip(image, 1)
    img_h, img_w, _ = image.shape
    results = face_mesh.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

    # Defaults
    status_color = (0, 255, 255)
    txt = "STARE AT CENTER & PRESS 'C'"
    dir_x, dir_y = "N/A", "N/A"

    if results.multi_face_landmarks:
        mesh_points = np.array([np.multiply([p.x, p.y], [img_w, img_h]).astype(int)
                                for p in results.multi_face_landmarks[0].landmark])

        # Eye landmarks
        l_iris, r_iris = mesh_points[468], mesh_points[473]
        l_inner, l_outer = mesh_points[133], mesh_points[33]
        l_top, l_bottom = mesh_points[159], mesh_points[145]
        r_inner, r_outer = mesh_points[362], mesh_points[263]
        r_top, r_bottom = mesh_points[386], mesh_points[374]

        # Calculate Raw Ratios
        raw_h = ((l_iris[0] - l_outer[0]) / (l_inner[0] - l_outer[0]) +
                 (r_iris[0] - r_outer[0]) / (r_inner[0] - r_outer[0])) / 2
        raw_v = ((l_iris[1] - l_top[1]) / (l_bottom[1] - l_top[1]) +
                 (r_iris[1] - r_top[1]) / (r_bottom[1] - r_top[1])) / 2

        # Smoothing
        history_h.append(raw_h)
        history_v.append(raw_v)
        h_ratio = sum(history_h) / len(history_h)
        v_ratio = sum(history_v) / len(history_v)

        # CALIBRATE
        if cv2.waitKey(1) & 0xFF == ord('c'):
            center_h, center_v = h_ratio, v_ratio
            calibrated = True
            print(f"Calibrated! Center: H={center_h:.2f}, V={center_v:.2f}")

        if calibrated:
            # Calculate distance from center
            h_diff = h_ratio - center_h
            v_diff = v_ratio - center_v

            # Logic: If you move past the threshold, you are OFF SCREEN
            on_screen = (abs(h_diff) < H_THRESHOLD) and (abs(v_diff) < V_THRESHOLD)

            # Directional labels
            dir_x = "Center"
            if h_diff < -0.02:
                dir_x = "Left"
            elif h_diff > 0.02:
                dir_x = "Right"

            dir_y = "Center"
            if v_diff < -0.015:
                dir_y = "Up"
            elif v_diff > 0.015:
                dir_y = "Down"

            status_color = (0, 255, 0) if on_screen else (0, 0, 255)
            txt = "ON SCREEN" if on_screen else "OFF SCREEN"

        # --- DRAWING ---
        cv2.putText(image, txt, (30, 50), cv2.FONT_HERSHEY_DUPLEX, 1, status_color, 2)
        if calibrated:
            cv2.putText(image, f"Gaze: {dir_y} {dir_x}", (30, 100), cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 255, 255), 1)

        # Visual markers for debugging
        cv2.circle(image, l_iris, 2, (255, 0, 255), -1)
        cv2.circle(image, r_iris, 2, (255, 0, 255), -1)

    cv2.imshow('Simplified Gaze Agent', image)
    if cv2.waitKey(1) & 0xFF == ord('q'): break

cap.release()
cv2.destroyAllWindows()
