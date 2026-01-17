import time
import threading
from screen_capture.screen_capture import capture_binary, send_to_webhook
from eye_tracking.eye_tracker import calibrate_eye_tracker, run_eye_tracker_stream
from orchestrate_webhook import send_to_webhook

CAPTURE_INTERVAL = 60  # seconds

def run_screen_capture():
    """Run screen capture every 5 seconds"""
    print("\n📸 Screen capture agent started")
    print(f"📊 Capturing every {CAPTURE_INTERVAL} seconds")
    print("-" * 50)

    while True:
        try:
            print("\n📸 Capturing screen...")
            image_bytes = capture_binary()
            send_to_webhook(image_bytes)
            print("✅ Screenshot sent")

        except Exception as e:
            print(f"❌ Screen capture error: {e}")

        time.sleep(CAPTURE_INTERVAL)


def main():
    print("🚀 Multi-capture system starting...")
    print("=" * 50)
    
    # STEP 1: Calibrate eye tracker (on main thread for GUI)
    print("\n📍 STEP 1: Eye Tracker Calibration")
    center_h, center_v = calibrate_eye_tracker()
    
    print(f"\n✅ Calibration complete! Values: H={center_h:.3f}, V={center_v:.3f}")
    print("\n" + "=" * 50)
    
    # STEP 2: Start screen capture in background thread
    print("📍 STEP 2: Starting background screen capture...")
    capture_thread = threading.Thread(
        target=run_screen_capture, 
        daemon=True
    )
    capture_thread.start()
    
    time.sleep(1)
    print("✅ Screen capture running in background")
    
    # STEP 3: Start eye tracker streaming (on main thread for GUI)
    print("\n📍 STEP 3: Starting eye tracker stream...")
    print("=" * 50)
    print("\n🎯 System fully operational!")
    print("Press 'Q' in the eye tracker window to stop\n")
    
    try:
        run_eye_tracker_stream(center_h, center_v)
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down...")
    
    print("\n👋 System stopped")


if __name__ == "__main__":
    main()