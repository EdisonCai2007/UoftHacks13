import cv2
import numpy as np
from collections import deque
import time
import mediapipe as mp
import json
import os

VIDEO_CAPTURE = 0
H_THRESHOLD, V_THRESHOLD = 0.04, 0.04
ALARM_DURATION = 15
MIN_LOOK_AWAY_DURATION = 3  # Default value

# Load MIN_LOOK_AWAY_DURATION from config.json if it exists
def load_config():
    """Load configuration from config.json, return default if not found"""
    config_file = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'config.json'))
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
            return config.get('MIN_LOOK_AWAY_DURATION', MIN_LOOK_AWAY_DURATION)
    except (FileNotFoundError, json.JSONDecodeError, KeyError):
        return MIN_LOOK_AWAY_DURATION

# Load the value at module import time
MIN_LOOK_AWAY_DURATION = load_config() 

# Initialize MediaPipe
def init_mediapipe():
    BaseOptions = mp.tasks.BaseOptions
    FaceLandmarker = mp.tasks.vision.FaceLandmarker
    FaceLandmarkerOptions = mp.tasks.vision.FaceLandmarkerOptions
    VisionRunningMode = mp.tasks.vision.RunningMode

    options = FaceLandmarkerOptions(
        base_options=BaseOptions(model_asset_path='face_landmarker.task'),
        running_mode=VisionRunningMode.VIDEO,
        num_faces=1
    )

    # Download model if needed
    if not os.path.exists('face_landmarker.task'):
        print("Downloading face landmarker model...")
        import urllib.request
        model_url = "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task"
        urllib.request.urlretrieve(model_url, "face_landmarker.task")
        print("Model downloaded!")

    return FaceLandmarker.create_from_options(options)


def calibrate_eye_tracker():
    """Calibration phase - returns calibration values"""
    print("\n👁️  CALIBRATION MODE")
    print("Look at the CENTER of your screen and press 'C' to calibrate")
    print("Press 'Q' when done\n")
    
    landmarker = init_mediapipe()
    cap = cv2.VideoCapture(VIDEO_CAPTURE)

    history_h = deque(maxlen=10)
    history_v = deque(maxlen=10)
    
    calibrated = False
    center_h, center_v = 0.5, 0.45
    frame_timestamp_ms = 0

    while cap.isOpened():
        success, image = cap.read()
        if not success:
            break

        image = cv2.flip(image, 1)
        img_h, img_w, _ = image.shape

        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_image)

        results = landmarker.detect_for_video(mp_image, frame_timestamp_ms)
        frame_timestamp_ms += 33

        if results.face_landmarks:
            landmarks = results.face_landmarks[0]
            mesh_points = np.array([[int(lm.x * img_w), int(lm.y * img_h)] for lm in landmarks])

            l_iris, r_iris = mesh_points[468], mesh_points[473]
            l_inner, l_outer = mesh_points[133], mesh_points[33]
            l_top, l_bottom = mesh_points[159], mesh_points[145]
            r_inner, r_outer = mesh_points[362], mesh_points[263]
            r_top, r_bottom = mesh_points[386], mesh_points[374]

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
                    cv2.putText(image, "CALIBRATED! Press Q to continue", (30, 65), 
                               cv2.FONT_HERSHEY_DUPLEX, 1.2, (0, 255, 0), 2)
                else:
                    cv2.putText(image, "STARE AT CENTER & PRESS 'C'", (30, 65), 
                               cv2.FONT_HERSHEY_DUPLEX, 1.2, (0, 255, 255), 2)

        cv2.imshow('Calibration', image)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('c'):
            if results.face_landmarks and len(history_h) > 0:
                center_h, center_v = h_ratio, v_ratio
                calibrated = True
                print(f"✅ Calibrated! Center: H={center_h:.3f}, V={center_v:.3f}")
                
                # Save calibration
                with open('calibration.json', 'w') as f:
                    json.dump({'center_h': center_h, 'center_v': center_v}, f)
                
        elif key == ord('q'):
            if calibrated:
                break
            else:
                print("⚠️  Please calibrate first by pressing 'C'")

    cap.release()
    cv2.destroyAllWindows()
    landmarker.close()
    
    return center_h, center_v


def run_eye_tracker_stream(center_h=0.5, center_v=0.45, metrics=None):
    """
    Streaming phase - runs continuously with calibration values
    
    Args:
        center_h: Calibrated horizontal center value
        center_v: Calibrated vertical center value
        metrics: SessionMetrics object for tracking analytics (optional)
    """
    print("\n👁️  Eye tracker streaming started")
    
    landmarker = init_mediapipe()
    cap = cv2.VideoCapture(VIDEO_CAPTURE)

    history_h = deque(maxlen=10)
    history_v = deque(maxlen=10)

    off_screen_start_time = None
    alarm_triggered = False
    frame_timestamp_ms = 0
    
    # Track previous state to detect transitions
    was_looking_away = False
    look_away_tracked = False  # Flag to ensure we only track once per look away event

    while cap.isOpened():
        success, image = cap.read()
        if not success:
            break

        image = cv2.flip(image, 1)
        img_h, img_w, _ = image.shape

        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_image)

        results = landmarker.detect_for_video(mp_image, frame_timestamp_ms)
        frame_timestamp_ms += 33

        status_color = (0, 255, 255)
        txt = "TRACKING..."
        show_text = True

        if results.face_landmarks:
            landmarks = results.face_landmarks[0]
            mesh_points = np.array([[int(lm.x * img_w), int(lm.y * img_h)] for lm in landmarks])

            l_iris, r_iris = mesh_points[468], mesh_points[473]
            l_inner, l_outer = mesh_points[133], mesh_points[33]
            l_top, l_bottom = mesh_points[159], mesh_points[145]
            r_inner, r_outer = mesh_points[362], mesh_points[263]
            r_top, r_bottom = mesh_points[386], mesh_points[374]

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

                h_diff, v_diff = h_ratio - center_h, v_ratio - center_v
                on_screen = (abs(h_diff) < H_THRESHOLD) and (abs(v_diff) < V_THRESHOLD)

                if not on_screen:
                    # User is looking away
                    if off_screen_start_time is None:
                        off_screen_start_time = time.time()
                        was_looking_away = True

                    elapsed = time.time() - off_screen_start_time
                    
                    # Only start tracking after minimum duration threshold
                    if elapsed >= MIN_LOOK_AWAY_DURATION and not look_away_tracked:
                        if metrics:
                            metrics.start_look_away()
                        look_away_tracked = True

                    if elapsed > ALARM_DURATION:
                        alarm_triggered = True
                        status_color = (0, 0, 255)
                        txt = f"ALARM: RETURN TO SCREEN ({int(elapsed)}s)"
                        if int(time.time() * 2) % 2 == 0:
                            show_text = False
                    else:
                        status_color = (0, 165, 255)
                        txt = f"AWAY: {int(elapsed)}s"
                else:
                    # User is back on screen
                    if was_looking_away and look_away_tracked:
                        # Only track end if we started tracking (i.e., it was long enough)
                        if metrics:
                            metrics.end_look_away()
                    
                    # Reset all flags
                    off_screen_start_time, alarm_triggered = None, False
                    was_looking_away = False
                    look_away_tracked = False
                    status_color, txt = (0, 255, 0), "ON SCREEN"

                if alarm_triggered:
                    cv2.rectangle(image, (0, 0), (img_w, img_h), (0, 0, 255), 25)

                if show_text:
                    cv2.putText(image, txt, (30, 65), cv2.FONT_HERSHEY_DUPLEX, 1.2, status_color, 2)

        cv2.imshow('FlowState Visual Alarm', image)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            # If user was looking away when quitting and it was tracked, end that event
            if was_looking_away and look_away_tracked and metrics:
                metrics.end_look_away()
            break

    cap.release()
    cv2.destroyAllWindows()
    landmarker.close()


if __name__ == "__main__":
    center_h, center_v = calibrate_eye_tracker()
    run_eye_tracker_stream(center_h, center_v)