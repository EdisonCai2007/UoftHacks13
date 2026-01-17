import sys
import os

# Get the absolute path of the 'backend' folder
current_dir = os.path.dirname(os.path.abspath(__file__))
# Move up to the 'FlowState' root folder
project_root = os.path.dirname(current_dir)

if project_root not in sys.path:
    sys.path.append(project_root)

# Now Python can see 'frontend.buddy'
try:
    from frontend import buddy
except ImportError as e:
    print(f"Error: Could not find buddy.py. Looking in: {project_root}")
    print(f"Actual error: {e}")

import platform
import time
<<<<<<< Updated upstream
import json

# Test: http://localhost:5678/webhook-test/df35d481-1743-43ee-a4ed-6b478dd5763d
# Prod: http://localhost:5678/webhook/df35d481-1743-43ee-a4ed-6b478dd5763d


WEBHOOK_URL = "http://localhost:5678/webhook/df35d481-1743-43ee-a4ed-6b478dd5763d"
BUDDY_API_URL = "http://127.0.0.1:5000/data"  # Buddy's Flask endpoint
TIMEOUT = 15
USER_TASK = "Doing calculus math homework"

def send_to_webhook(image_bytes: bytes):
    files = {
        "file": ("screenshot.jpg", image_bytes, "image/jpeg")
    }
    data = {
        "current_task": USER_TASK,
        "timestamp": int(time.time())
    }

    response = requests.post(
        WEBHOOK_URL,
        files=files,
        data=data,
        timeout=TIMEOUT
    )

    result = response.json()
    print(f"📦 n8n response: {result}")

    # Send to Buddy's Flask API
    try:
        buddy_response = requests.post(
            BUDDY_API_URL,
            json={
                "animation": result.get("animation", "idle"),
                "message": result.get("message", ""),
                "is_focused": result.get("is_focused", True)
            },
            timeout=2
        )
        print(f"🦌 Buddy updated: {buddy_response.json()}")
    except Exception as e:
        print(f"⚠️  Failed to update Buddy: {e}")

    response.raise_for_status()
    return result
=======
import threading
import tkinter as tk
from tkinter import messagebox, simpledialog
import requests

# ================= CONFIG =================
WEBHOOK_URL = "http://localhost:5678/webhook-test/df35d481-1743-43ee-a4ed-6b478dd5763d"
TIMEOUT = 30
USER_TASKS = []
IS_MAC = platform.system() == "Darwin"

class TaskInputDialog:
    """Styled dialog that works on both Windows and macOS."""
    def __init__(self, parent):
        self.result = []
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("FlowState Tasks")
        self.dialog.geometry("500x600")
        
        # Colors & Fonts
        self.bg_color = "#1e293b"
        self.text_bg = "#334155"
        self.accent_color = "#38bdf8"
        self.font_main = "Alice" if not IS_MAC else "Optima" # Fallback for Mac

        self.dialog.config(bg=self.bg_color)
        self.dialog.transient(parent)
        self.dialog.grab_set()

        # UI Elements
        tk.Label(self.dialog, text="What are you working on?", 
                 font=(self.font_main, 16, "bold"), bg=self.bg_color, 
                 fg=self.accent_color, pady=15).pack()

        text_frame = tk.Frame(self.dialog, bg=self.bg_color)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=10)

        self.text_area = tk.Text(text_frame, font=("Arial", 12), bg=self.text_bg, 
                                 fg="white", insertbackground="white", padx=10, pady=10, bd=0)
        self.text_area.pack(fill=tk.BOTH, expand=True)
        
        # Bindings
        self.text_area.bind("<FocusIn>", self.clear_placeholder)
        # Cross-platform Submit Shortcut: Cmd+Enter (Mac) or Ctrl+Enter (Windows)
        shortcut = "<Meta-Return>" if IS_MAC else "<Control-Return>"
        self.dialog.bind(shortcut, lambda e: self.submit())

        # Buttons
        btn_frame = tk.Frame(self.dialog, bg=self.bg_color)
        btn_frame.pack(pady=20)

        tk.Button(btn_frame, text="Add Tasks", command=self.submit, bg=self.accent_color,
                  fg="#0f172a", font=(self.font_main, 11, "bold"), padx=20).pack(side=tk.LEFT, padx=10)
        
        tk.Button(btn_frame, text="Cancel", command=self.cancel, bg="#475569",
                  fg="white", font=(self.font_main, 11), padx=20).pack(side=tk.LEFT, padx=10)

        # Helper label for shortcut
        hint = "⌘ + Enter" if IS_MAC else "Ctrl + Enter"
        tk.Label(self.dialog, text=f"Shortcut: {hint}", bg=self.bg_color, fg="#64748b", font=("Arial", 8)).pack()

    def clear_placeholder(self, event):
        if "e.g.," in self.text_area.get("1.0", tk.END):
            self.text_area.delete("1.0", tk.END)
            self.text_area.config(fg="white")

    def submit(self):
        content = self.text_area.get("1.0", tk.END).strip()
        if content:
            self.result = [l.strip() for l in content.split("\n") if l.strip()]
            self.dialog.master.quit() # This breaks the mainloop safely

    def cancel(self):
        self.result = []
        self.dialog.master.quit()

def get_user_tasks():
    """A version that forces the window to exist and handle events."""
    global USER_TASKS
    
    root = tk.Tk()
    # On Windows, setting alpha to 0 hides the root without 'withdrawing' 
    # which sometimes causes the popup to inherit the 'hidden' state.
    root.attributes('-alpha', 0) 
    
    # Initialize the dialog
    input_dialog = TaskInputDialog(root)

    # This function will run AFTER the window is fully drawn
    def force_focus():
        input_dialog.dialog.after(200, lambda: input_dialog.dialog.focus_force())
        input_dialog.dialog.after(200, lambda: input_dialog.text_area.focus_set())

    # Update submit to quit the loop
    original_submit = input_dialog.submit
    def final_submit():
        original_submit()
        if input_dialog.result:
            root.quit() # This exits mainloop
    input_dialog.submit = final_submit

    root.after(100, force_focus)
    
    # On Windows, this is the only way to keep the window alive
    root.mainloop() 
    
    tasks = input_dialog.result
    root.destroy()
    return tasks

def send_to_webhook(image_bytes: bytes):
    if not USER_TASKS: return
    files = {"file": ("screenshot.jpg", image_bytes, "image/jpeg")}
    data = {"current_task": ", ".join(USER_TASKS), "timestamp": int(time.time())}
    try:
        requests.post(WEBHOOK_URL, files=files, data=data, timeout=TIMEOUT)
    except Exception as e:
        print(f"Webhook error: {e}")

# ================= MAIN EXECUTION =================
if __name__ == "__main__":
    # 1. Run the popup first (Stops here until you hit Add Tasks)
    tasks = get_user_tasks()
    
    if not tasks:
        print("No tasks entered. Exiting.")
        sys.exit()
    
    # 2. ONLY AFTER popup closes, start the Moose
    print(f"Starting Moose with tasks: {USER_TASKS}")
    
    # Use a thread for the moose so the main script can keep running
    moose_thread = threading.Thread(target=buddy.start_moose, daemon=True)
    moose_thread.start()
    
    # Keep the main script alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nExiting...")

>>>>>>> Stashed changes
