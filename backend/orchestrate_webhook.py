import requests
import time

# Test: http://localhost:5678/webhook-test/df35d481-1743-43ee-a4ed-6b478dd5763d
# Prod: http://localhost:5678/webhook/df35d481-1743-43ee-a4ed-6b478dd5763d


WEBHOOK_URL = "http://localhost:5678/webhook/df35d481-1743-43ee-a4ed-6b478dd5763d"
BUDDY_API_URL = "http://127.0.0.1:5000/data"  # Buddy's Flask endpoint
TIMEOUT = 15

def send_to_webhook(image_bytes: bytes, user_task: str):
    files = {
        "file": ("screenshot.jpg", image_bytes, "image/jpeg")
    }
    data = {
        "current_task": user_task,
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