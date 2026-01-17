import time
import threading
import subprocess
import tkinter as tk
from datetime import datetime
from screen_capture.screen_capture import capture_binary
from eye_tracking.eye_tracker import calibrate_eye_tracker, run_eye_tracker_stream
from orchestrate_webhook import send_to_webhook
from user_onboarding import TaskInputDialog
from amplitude_service.amplitude_service import track_session_start, track_session_end, track_tab_switch, track_look_away, generate_session_id


CAPTURE_INTERVAL = 15  # seconds
USER_TASK, USER_FRIENDS, USER_FOOD = "","",""

# ========================
# ANALYTICS TRACKING VARIABLES
# ========================
class SessionMetrics:
    """Track session metrics for Amplitude analytics"""
    def __init__(self):
        self.session_id = generate_session_id()
        self.start_time = None
        self.tab_switch_count = 0
        self.look_away_count = 0
        self.total_look_away_duration = 0  # in seconds
        self.last_look_away_start = None
        
    def increment_tab_switch(self):
        """Increment tab switch counter and track event"""
        self.tab_switch_count += 1
        track_tab_switch(session_id=self.session_id)
        print(f"📊 Tab switches: {self.tab_switch_count}")
    
    def start_look_away(self):
        """Mark the start of a look away event"""
        self.last_look_away_start = time.time()
    
    def end_look_away(self):
        """Mark the end of a look away event and track it"""
        if self.last_look_away_start:
            duration = time.time() - self.last_look_away_start
            self.look_away_count += 1
            self.total_look_away_duration += duration
            track_look_away(session_id=self.session_id, duration_seconds=duration)
            print(f"📊 Look aways: {self.look_away_count} (Total: {self.total_look_away_duration:.1f}s)")
            self.last_look_away_start = None
    
    def get_session_duration(self):
        """Calculate total session duration in seconds"""
        if self.start_time:
            return int(time.time() - self.start_time)
        return 0

# Global metrics object
metrics = SessionMetrics()


def run_screen_capture():
    """Run screen capture every 15 seconds"""
    print("\n📸 Screen capture agent started")
    print(f"📊 Capturing every {CAPTURE_INTERVAL} seconds")
    print("-" * 50)

    while True:
        try:
            image_bytes = capture_binary()
            print(f"✅ Screenshot sent {USER_TASK}")
            send_to_webhook(image_bytes, USER_TASK)

        except Exception as e:
            print(f"❌ Screen capture error: {e}")

        time.sleep(CAPTURE_INTERVAL)

def start_buddy():
    """Start the test.py moose in a separate process"""
    print("🦌 Starting Buddy Moose...")
    
    buddy_process = subprocess.Popen(
        ["python3", "../frontend/test.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    print(f"✅ Buddy started (PID: {buddy_process.pid})")
    return buddy_process

def main():
    print("🚀 Multi-capture system starting...")
    print("=" * 50)
    
    # STEP 0: Get user tasks - INLINE
    print("\n📍 STEP 0: Task Setup")
    root = tk.Tk()
    root.overrideredirect(True)  # Remove window decorations
    root.geometry("0x0")  # Make it invisible
    root.attributes('-alpha', 0)  # Transparent

    dialog = TaskInputDialog(root)
    root.mainloop()  # Wait for user input

    global USER_TASK, USER_FRIENDS, USER_FOOD
    USER_TASK = dialog.result
    USER_FRIENDS = dialog.with_friends
    USER_FOOD = dialog.with_food
    
    root.quit()
    root.destroy()
    
    print("\n" + "=" * 50)
    
    # STEP 1: Start Buddy Moose
    print("\n📍 STEP 1: Starting Buddy Moose")
    buddy_process = start_buddy()
    time.sleep(2)
    
    # STEP 2: Calibrate eye tracker
    print("\n📍 STEP 2: Eye Tracker Calibration")
    center_h, center_v = calibrate_eye_tracker()
    
    print(f"\n✅ Calibration complete! Values: H={center_h:.3f}, V={center_v:.3f}")
    print("\n" + "=" * 50)

    time.sleep(2)
    
    # STEP 2.5: Track session start with Amplitude
    print("\n📍 STEP 2.5: Starting Amplitude session tracking...")
    metrics.start_time = time.time()
    track_session_start(
        session_id=metrics.session_id,
        task=USER_TASK,
        with_friends=USER_FRIENDS,
        with_food=USER_FOOD
    )
    print(f"✅ Session tracked: {metrics.session_id}")
    print("=" * 50)
    
    # STEP 3: Start screen capture in background thread
    print("\n📍 STEP 3: Starting background screen capture...")
    capture_thread = threading.Thread(
        target=run_screen_capture, 
        daemon=True
    )
    capture_thread.start()
    
    time.sleep(1)
    print("✅ Screen capture thread started")
    print(f"🔍 Thread alive: {capture_thread.is_alive()}")
    
    # STEP 4: Start eye tracker streaming
    print("\n📍 STEP 4: Starting eye tracker stream...")
    print("=" * 50)
    print("\n🎯 System fully operational!")
    print("Press 'Q' in the eye tracker window to stop\n")
    
    try:
        # TODO: Modify run_eye_tracker_stream to accept callbacks for:
        # - metrics.increment_tab_switch() when tab switches detected
        # - metrics.start_look_away() when user looks away
        # - metrics.end_look_away() when user looks back
        run_eye_tracker_stream(center_h, center_v)
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down...")
    finally:
        # Track session end before cleanup
        session_duration = metrics.get_session_duration()
        track_session_end(
            session_id=metrics.session_id,
            duration=session_duration
        )
        
        # Print final metrics
        print("\n" + "=" * 50)
        print("📊 SESSION SUMMARY")
        print("=" * 50)
        print(f"Duration: {session_duration}s ({session_duration/60:.1f} minutes)")
        print(f"Tab Switches: {metrics.tab_switch_count}")
        print(f"Look Aways: {metrics.look_away_count}")
        print(f"Total Look Away Time: {metrics.total_look_away_duration:.1f}s")
        print("=" * 50)
        
        if buddy_process.poll() is None:
            print("🦌 Stopping Buddy...")
            buddy_process.terminate()
            buddy_process.wait(timeout=5)
    
    print("\n👋 System stopped")


if __name__ == "__main__":
    main()