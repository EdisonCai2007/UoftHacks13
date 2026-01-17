import time
import threading
import subprocess
from screen_capture.screen_capture import capture_binary
from eye_tracking.eye_tracker import calibrate_eye_tracker, run_eye_tracker_stream
from orchestrate_webhook import send_to_webhook

CAPTURE_INTERVAL = 15  # seconds

def run_screen_capture():
    """Run screen capture every 5 seconds"""
    print("\n📸 Screen capture agent started")
    print(f"📊 Capturing every {CAPTURE_INTERVAL} seconds")
    print("-" * 50)

    while True:
        try:
            image_bytes = capture_binary()
            print("✅ Screenshot sent")
            send_to_webhook(image_bytes)

        except Exception as e:
            print(f"❌ Screen capture error: {e}")

        time.sleep(CAPTURE_INTERVAL)

def start_buddy():
    """Start the buddy.py moose in a separate process"""
    print("🦌 Starting Buddy Moose...")
    
    # Adjust path to where your buddy.py is located
    buddy_process = subprocess.Popen(
        ["python", "../frontend/buddy.py"],  # Update path as needed
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    print(f"✅ Buddy started (PID: {buddy_process.pid})")
    return buddy_process

def main():
    print("🚀 Multi-capture system starting...")
    print("=" * 50)
    
    # STEP 0: Start Buddy Moose
    print("\n📍 STEP 0: Starting Buddy Moose")
    buddy_process = start_buddy()
    time.sleep(2)  # Give buddy time to open window
    
    # STEP 1: Calibrate eye tracker (on main thread for GUI)
    print("\n📍 STEP 1: Eye Tracker Calibration")
    center_h, center_v = calibrate_eye_tracker()
    
    print(f"\n✅ Calibration complete! Values: H={center_h:.3f}, V={center_v:.3f}")
    print("\n" + "=" * 50)

    time.sleep(2)
    
    # STEP 2: Start screen capture in background thread
    print("📍 STEP 2: Starting background screen capture...")
    capture_thread = threading.Thread(
        target=run_screen_capture, 
        daemon=True
    )
    capture_thread.start()
    
    time.sleep(1)
    print("✅ Screen capture thread started")
    print(f"🔍 Thread alive: {capture_thread.is_alive()}")
    
    # STEP 3: Start eye tracker streaming (on main thread for GUI)
    print("\n📍 STEP 3: Starting eye tracker stream...")
    print("=" * 50)
    print("\n🎯 System fully operational!")
    print("Press 'Q' in the eye tracker window to stop\n")
    
    try:
        run_eye_tracker_stream(center_h, center_v)
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down...")
    finally:
        # Clean up buddy process
        if buddy_process.poll() is None:  # Still running
            print("🦌 Stopping Buddy...")
            buddy_process.terminate()
            buddy_process.wait(timeout=5)
    
    print("\n👋 System stopped")


if __name__ == "__main__":
    main()