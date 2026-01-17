import tkinter as tk
from PIL import Image, ImageTk
import os
import threading
import subprocess
import requests
import platform
import math
from flask import Flask, request, jsonify

# ========================
# CONFIGURATION
# ========================
IMAGE_PATH_1 = os.path.expanduser("../assets/moose1.png")
IMAGE_PATH_2 = os.path.expanduser("../assets/moose2.png")
WINDOW_WIDTH = 150 
WINDOW_HEIGHT = 200 # Extra room for the bubble
START_X = 1000
BASE_Y = 700
MOVE_STEP = 4
FRAME_DELAY = 50
ANIMATION_SPEED = 100
LEAP_HEIGHT = 40
SCREEN_RIGHT_EDGE = 1400

# Transparency Key - This color becomes a "hole" in the window
TRANS_COLOR = "white" 

# GLOBAL STATE
current_animation = "walk"
current_message = ""

# ========================
# FLASK SERVER
# ========================
app = Flask(__name__)

@app.route('/data', methods=['POST'])
def receive_data():
    global current_animation, current_message
    data = request.json
    if data:
        current_animation = data.get("animation")
        current_message = data.get("message", "")
        
        # UI updates must happen on the main thread
        window.after(0, update_bubble_ui)
        
        if current_animation == "talk" and current_message:
            threading.Thread(target=speak, args=(current_message,), daemon=True).start()
            
    return jsonify({"status": "ok"}), 200

def update_bubble_ui():
    """Removes the label widget entirely when not talking."""
    if current_animation == "talk" and current_message.strip():
        msg_label.config(
            text=current_message,
            bg="#fffffe",      # NOT pure white, so it stays visible on black screens
            fg="#1a1a1a",      # Dark grey text for readability
            highlightthickness=2,
            highlightbackground="#d1d1d1", # Light border
            padx=10, pady=8
        )
        msg_label.pack(side="top", pady=10)
    else:
        # This removes the widget and its 'space' from the window
        msg_label.pack_forget()

def run_server():
    app.run(host='127.0.0.1', port=5000, debug=False, use_reloader=False)

# ========================
# SPEECH
# ========================
def speak(text: str):
    try:
        if platform.system() == "Windows":
            clean_text = text.replace("'", "")
            cmd = f"Add-Type –AssemblyName System.Speech; (New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak('{clean_text}')"
            subprocess.run(["powershell", "-Command", cmd])
        else:
            subprocess.run(["say", text])
    except:
        pass

# ========================
# INITIALIZE WINDOW
# ========================
window = tk.Tk()
window.overrideredirect(True)
window.attributes("-topmost", True)
window.config(bg=TRANS_COLOR) # Set the window floor to the 'hole' color

if platform.system() == "Windows":
    window.attributes("-transparentcolor", TRANS_COLOR)
else:
    window.attributes("-transparent", True)

window.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}+{START_X}+{BASE_Y}")

# Message Label (Created but not packed)
msg_label = tk.Label(
    window, 
    text="", 
    font=("Arial", 10, "bold"), 
    wraplength=130,
    justify="center",
    bd=0
)

# Load Images
img1_original = Image.open(IMAGE_PATH_1).resize((100, 100), Image.Resampling.LANCZOS)
img2_original = Image.open(IMAGE_PATH_2).resize((100, 100), Image.Resampling.LANCZOS)

moose_image2_left = ImageTk.PhotoImage(img2_original)
moose_image2_right = ImageTk.PhotoImage(img2_original.transpose(Image.FLIP_LEFT_RIGHT))

# Moose label must also use the TRANS_COLOR as its background
label = tk.Label(window, image=moose_image2_left, bd=0, bg=TRANS_COLOR)
label.pack(side="bottom")

# ========================
# ANIMATION LOGIC
# ========================
x, y = START_X, BASE_Y
direction, leap_progress = -1, 0

def animate_frames():
    if current_animation == "walk":
        if y != BASE_Y:
            rotation_angle = (leap_progress - 0.5) * 50
            img = img1_original if direction == 1 else img1_original.transpose(Image.FLIP_LEFT_RIGHT)
            # Ensure the rotated "empty space" is filled with the transparency key
            rotated = img.rotate(rotation_angle, expand=False, fillcolor=TRANS_COLOR)
            photo = ImageTk.PhotoImage(rotated)
            label.config(image=photo)
            label.image = photo
        else:
            label.config(image=moose_image2_left if direction == 1 else moose_image2_right)
    else:
        label.config(image=moose_image2_left if direction == 1 else moose_image2_right)
    window.after(ANIMATION_SPEED, animate_frames)

def move_buddy():
    global x, y, direction, leap_progress
    if current_animation == "walk":
        x += MOVE_STEP * direction
        if x < 0 or x > SCREEN_RIGHT_EDGE: direction *= -1
        leap_progress += 0.1
        if leap_progress > 1: leap_progress = 0
        y = BASE_Y - int(math.sin(leap_progress * math.pi) * LEAP_HEIGHT)
    else:
        y = BASE_Y
    window.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}+{x}+{y}")
    window.after(FRAME_DELAY, move_buddy)

# ========================
# MAIN
# ========================
if __name__ == "__main__":
    threading.Thread(target=run_server, daemon=True).start()
    animate_frames()
    move_buddy()
    window.mainloop()