import tkinter as tk
from PIL import Image, ImageTk
import os
import threading
import subprocess
from flask import Flask, request, jsonify
import requests

# ========================
# CONFIGURATION
# ========================
IMAGE_PATH = os.path.expanduser("../assets/buddy.png")
WINDOW_WIDTH = 100
WINDOW_HEIGHT = 100
START_X = 1000
START_Y = 500
MOVE_STEP = 5
FRAME_DELAY = 50
SCREEN_RIGHT_EDGE = 1400  # adjust if needed
VOICE_COMMAND = ["say"]   # macOS TTS

# N8N CONFIG
N8N_URL = "http://localhost:5678/webhook-test/d27e5cc4-8c6a-4609-ba24-9b24ce4a700b"  # Replace with your n8n webhook URL
PING_INTERVAL = 5  # seconds

# ========================
# SPEECH
# ========================
def speak(text: str):
    subprocess.run(VOICE_COMMAND + [text])

# ========================
# N8N PING
# ========================
def ping_n8n():
    try:
        response = requests.get(N8N_URL, timeout=5)
        print("Pinged n8n, status:", response.status_code)
    except Exception as e:
        print("Failed to ping n8n:", e)
    finally:
        # Schedule next ping
        threading.Timer(PING_INTERVAL, ping_n8n).start()

# ========================
# INITIALIZE WINDOW
# ========================
window = tk.Tk()
window.overrideredirect(True)
window.attributes("-topmost", True)
window.attributes("-transparent", True)
window.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}+{START_X}+{START_Y}")

# Load image
img = Image.open(IMAGE_PATH)
img = img.resize((WINDOW_WIDTH, WINDOW_HEIGHT), Image.Resampling.LANCZOS)
buddy_image = ImageTk.PhotoImage(img)

label = tk.Label(window, image=buddy_image, bd=0, bg="black")
label.pack()

# ========================
# MOVEMENT LOGIC
# ========================
x = START_X
direction = -1  # -1 = left, 1 = right

def move_buddy():
    global x, direction

    x += MOVE_STEP * direction

    if x < 0 or x > SCREEN_RIGHT_EDGE:
        direction *= -1

    window.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}+{x}+{START_Y}")
    window.after(FRAME_DELAY, move_buddy)

# ========================
# START EVERYTHING
# ========================
ping_n8n()          # start n8n pings
move_buddy()         # start movement
window.mainloop()
