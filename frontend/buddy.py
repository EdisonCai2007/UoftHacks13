import tkinter as tk
from PIL import Image, ImageTk
import os
import threading
import subprocess
import requests
import platform
import math

# ========================
# CONFIGURATION
# ========================
IMAGE_PATH_1 = os.path.expanduser("../assets/moose1.png")
IMAGE_PATH_2 = os.path.expanduser("../assets/moose2.png")
WINDOW_WIDTH = 100
WINDOW_HEIGHT = 100
START_X = 1000
BASE_Y = 800  # Base position at bottom of screen
MOVE_STEP = 4
FRAME_DELAY = 50
ANIMATION_SPEED = 100  # milliseconds between frame switches
LEAP_HEIGHT = 40  # How high the moose jumps
SCREEN_RIGHT_EDGE = 1400  # adjust if needed
VOICE_COMMAND = ["say"]  # macOS TTS

# N8N CONFIG
N8N_ENABLED = False  # Set to True when n8n is running
N8N_URL = "http://localhost:5678/webhook-test/d27e5cc4-8c6a-4609-ba24-9b24ce4a700b"
PING_INTERVAL = 5  # seconds


# ========================
# SPEECH
# ========================
def speak(text: str):
    """Text-to-speech function."""
    subprocess.run(VOICE_COMMAND + [text])


# ========================
# N8N PING
# ========================
def ping_n8n():
    """Ping n8n webhook periodically."""
    if not N8N_ENABLED:
        return

    try:
        response = requests.get(N8N_URL, timeout=5)
        print("Pinged n8n, status:", response.status_code)
    except Exception as e:
        print("Failed to ping n8n:", e)
    finally:
        # Schedule next ping only if enabled
        if N8N_ENABLED:
            threading.Timer(PING_INTERVAL, ping_n8n).start()


# ========================
# INITIALIZE WINDOW
# ========================
window = tk.Tk()
window.overrideredirect(True)
window.attributes("-topmost", True)

# Make window transparent (platform specific)
if platform.system() == "Windows":
    window.attributes("-transparentcolor", "white")
else:
    window.attributes("-transparent", True)

window.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}+{START_X}+{BASE_Y}")

# Load both moose images (keep original PIL images for rotation)
img1_original = Image.open(IMAGE_PATH_1)
img1_original = img1_original.resize((WINDOW_WIDTH, WINDOW_HEIGHT), Image.Resampling.LANCZOS)

img2_original = Image.open(IMAGE_PATH_2)
img2_original = img2_original.resize((WINDOW_WIDTH, WINDOW_HEIGHT), Image.Resampling.LANCZOS)

# Pre-create the static moose2 images
moose_image2_left = ImageTk.PhotoImage(img2_original)
moose_image2_right = ImageTk.PhotoImage(img2_original.transpose(Image.FLIP_LEFT_RIGHT))

label = tk.Label(window, image=moose_image2_left, bd=0, bg="white")
label.pack()

# ========================
# ANIMATION STATE
# ========================
x = START_X
y = BASE_Y
direction = -1  # -1 = left, 1 = right
current_frame = 0  # 0 or 1 for alternating frames
leap_progress = 0  # 0 to 1, tracks position in leap cycle


def animate_frames():
    """Alternate between the two moose frames for hopping animation."""
    global current_frame

    current_frame = 1 - current_frame  # Toggle between 0 and 1

    # Check if moose is in the air (jumping)
    if y != BASE_Y:  # Moose is jumping
        # Calculate rotation angle based on leap progress
        # When going up (0 to 0.5), angle is positive (tilting forward)
        # When going down (0.5 to 1), angle is negative (tilting backward)
        rotation_angle = (leap_progress - 0.5) * 50  # -25 to +25 degrees

        # Determine which image to use based on direction
        if direction == 1:  # Moving left
            img_to_rotate = img1_original
        else:  # Moving right
            img_to_rotate = img1_original.transpose(Image.FLIP_LEFT_RIGHT)
            rotation_angle = rotation_angle  # Flip rotation for right direction

        # Rotate the image
        rotated = img_to_rotate.rotate(rotation_angle, expand=False, fillcolor=(255, 255, 255))
        rotated_photo = ImageTk.PhotoImage(rotated)
        label.config(image=rotated_photo)
        label.image = rotated_photo  # Keep reference to prevent garbage collection
    else:  # Moose is on the ground
        if direction == 1:  # Moving left
            label.config(image=moose_image2_left)
        else:  # Moving right
            label.config(image=moose_image2_right)

    window.after(ANIMATION_SPEED, animate_frames)


def move_buddy():
    """Move moose across screen with leaping motion."""
    global x, y, direction, leap_progress

    # Horizontal movement
    x += MOVE_STEP * direction

    if x < 0 or x > SCREEN_RIGHT_EDGE:
        direction *= -1

    # Leaping motion (sine wave for smooth arc)
    leap_progress += 0.1
    if leap_progress > 1:
        leap_progress = 0

    # Calculate Y position using sine wave (creates arc)
    # When leap_progress = 0.5, moose is at highest point
    y_offset = math.sin(leap_progress * math.pi) * LEAP_HEIGHT
    y = BASE_Y - int(y_offset)

    window.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}+{x}+{y}")
    window.after(FRAME_DELAY, move_buddy)


# ========================
# START EVERYTHING
# ========================
if N8N_ENABLED:
    ping_n8n()  # start n8n pings
animate_frames()  # start frame animation
move_buddy()  # start movement with leaping
window.mainloop()
