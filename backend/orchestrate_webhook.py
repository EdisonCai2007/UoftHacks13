import requests
import time

# ================= CONFIG =================

WEBHOOK_URL = "http://localhost:5678/webhook-test/df35d481-1743-43ee-a4ed-6b478dd5763d"
TIMEOUT = 30                     # seconds

USER_TASK = "Doing calculus math homework"

# =========================================

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

    print(response.json())

    response.raise_for_status()