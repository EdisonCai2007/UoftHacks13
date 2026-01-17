import cv2
import numpy as np
from collections import deque
import time
import mediapipe as mp

# Initialize MediaPipe Face Mesh for version 0.10.x
BaseOptions = mp.tasks.BaseOptions
FaceLandmarker = mp.tasks.vision.FaceLandmarker
FaceLandmarkerOptions = mp.tasks.vision.FaceLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode

# Create FaceLandmarker
options = FaceLandmarkerOptions(
    base_options=BaseOptions(model_asset_path='face_landmarker.task'),
    running_mode=VisionRunningMode.VIDEO,
    num_faces=1
)

# Download the model file first
print("Downloading face landmarker model...")
import urllib.request

model_url = "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task"
urllib.request.urlretrieve(model_url, "face_landmarker.task")
print("Model downloaded!")

landmarker = FaceLandmarker.create_from_options(options)

cap = cv2.VideoCapture(1)

history_h = deque(maxlen=10)
history_v = deque(maxlen=10)

# --- SETTINGS ---
calibrated = False
center_h, center_v = 0.5, 0.45
H_THRESHOLD, V_THRESHOLD = 0.04, 0.04
ALARM_DURATION = 30

# Timer & Visual States
off_screen_start_time = None
alarm_triggered = False
frame_timestamp_ms = 0

print("Look at the CENTER and press 'C' to calibrate.")

while cap.isOpened():
    success, image = cap.read()
    if not success:
        break

    image = cv2.flip(image, 1)
    img_h, img_w, _ = image.shape

    # Convert to RGB and create MediaPipe Image
    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_image)

    # Process with timestamp
    results = landmarker.detect_for_video(mp_image, frame_timestamp_ms)
    frame_timestamp_ms += 33  # ~30 fps

    status_color = (0, 255, 255)
    txt = "STARE AT CENTER & PRESS 'C'"
    show_text = True

    if results.face_landmarks:
        landmarks = results.face_landmarks[0]
        mesh_points = np.array([[int(lm.x * img_w), int(lm.y * img_h)] for lm in landmarks])

        # Iris Landmarks
        l_iris, r_iris = mesh_points[468], mesh_points[473]
        l_inner, l_outer = mesh_points[133], mesh_points[33]
        l_top, l_bottom = mesh_points[159], mesh_points[145]
        r_inner, r_outer = mesh_points[362], mesh_points[263]
        r_top, r_bottom = mesh_points[386], mesh_points[374]

        # Calculate Gaze (with division by zero protection)
        l_h_range = l_inner[0] - l_outer[0]
        r_h_range = r_inner[0] - r_outer[0]
        l_v_range = l_bottom[1] - l_top[1]
        r_v_range = r_bottom[1] - r_top[1]

        if l_h_range != 0 and r_h_range != 0 and l_v_range != 0 and r_v_range != 0:
            raw_h = ((l_iris[0] - l_outer[0]) / l_h_range +
                     (r_iris[0] - r_outer[0]) / r_h_range) / 2
            raw_v = ((l_iris[1] - l_top[1]) / l_v_range +
                     (r_iris[1] - r_top[1]) / r_v_range) / 2

            history_h.append(raw_h)
            history_v.append(raw_v)
            h_ratio, v_ratio = sum(history_h) / len(history_h), sum(history_v) / len(history_v)

            if calibrated:
                h_diff, v_diff = h_ratio - center_h, v_ratio - center_v
                on_screen = (abs(h_diff) < H_THRESHOLD) and (abs(v_diff) < V_THRESHOLD)

                if not on_screen:
                    if off_screen_start_time is None:
                        off_screen_start_time = time.time()

                    elapsed = time.time() - off_screen_start_time

                    if elapsed > ALARM_DURATION:
                        alarm_triggered = True
                        status_color = (0, 0, 255)  # Red
                        txt = f"ALARM: RETURN TO SCREEN ({int(elapsed)}s)"
                        # Flash text every 0.5s
                        if int(time.time() * 2) % 2 == 0:
                            show_text = False
                    else:
                        status_color = (0, 165, 255)  # Orange
                        txt = f"AWAY: {int(elapsed)}s"
                else:
                    off_screen_start_time, alarm_triggered = None, False
                    status_color, txt = (0, 255, 0), "ON SCREEN"

            # --- DRAWING ---
            if alarm_triggered:
                cv2.rectangle(image, (0, 0), (img_w, img_h), (0, 0, 255), 25)

            if show_text:
                cv2.putText(image, txt, (30, 65), cv2.FONT_HERSHEY_DUPLEX, 1.2, status_color, 2)

    cv2.imshow('FlowState Visual Alarm', image)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('c'):
        if results.face_landmarks and len(history_h) > 0:
            center_h, center_v = h_ratio, v_ratio
            calibrated = True
            print(f"Calibrated! Center: H={center_h:.3f}, V={center_v:.3f}")
    elif key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
landmarker.close()
