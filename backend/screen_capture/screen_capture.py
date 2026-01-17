import time
import requests
from io import BytesIO
from PIL import Image
import mss

# ================= CONFIG =================

WEBHOOK_URL = "http://localhost:5678/webhook-test/df35d481-1743-43ee-a4ed-6b478dd5763d"
CAPTURE_INTERVAL = 5            # seconds
JPEG_QUALITY = 60               # 40–70 recommended
MAX_WIDTH = 1280                # downscale for cost/perf
TIMEOUT = 5                     # seconds

USER_TASK = "Doing calculus math homework"

# =========================================


def capture_binary() -> bytes:
    """Capture full screen and return JPEG bytes."""
    with mss.mss() as sct:
        monitor = sct.monitors[1]  # Primary monitor
        screenshot = sct.grab(monitor)

        img = Image.frombytes(
            "RGB",
            screenshot.size,
            screenshot.rgb
        )

        # Resize while preserving aspect ratio
        if img.width > MAX_WIDTH:
            ratio = MAX_WIDTH / img.width
            img = img.resize(
                (MAX_WIDTH, int(img.height * ratio)),
                Image.LANCZOS
            )

        buffer = BytesIO()
        img.save(
            buffer,
            format="JPEG",
            quality=JPEG_QUALITY,
            optimize=True
        )

        return buffer.getvalue()


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

    response.raise_for_status()


def main():
    print("📸 Screen capture agent started")

    while True:
        try:
            image_bytes = capture_binary()
            send_to_webhook(image_bytes)
            print("✅ Screenshot sent (binary)")

        except Exception as e:
            print(f"❌ Error: {e}")

        time.sleep(CAPTURE_INTERVAL)


if __name__ == "__main__":
    main()