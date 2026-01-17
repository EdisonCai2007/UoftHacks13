import requests
import time
import random

# The local address where buddy.py is listening
BUDDY_URL = "http://127.0.0.1:5000/data"

def send_to_buddy(animation, message, is_focused):
    """Sends the formatted JSON payload to buddy.py"""
    payload = {
        "animation": animation,
        "message": message,
        "is_focused": is_focused
    }

    try:
        # Use the 'json' parameter to automatically set headers and encode data
        response = requests.post(BUDDY_URL, json=payload, timeout=5)
        
        if response.status_code == 200:
            print(f"✅ Sent: [{animation}] '{message}' (Focused: {is_focused})")
        else:
            print(f"❌ Buddy.py responded with error code: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("⚠️ Connection Error: Is buddy.py running in another terminal?")
    except Exception as e:
        print(f"⚠️ An unexpected error occurred: {e}")

def run_auto_test():
    """Runs a loop to send random updates every 3 seconds"""
    animations = ["walk", "talk", "idle"]
    messages = [
        "Scanning the perimeter...",
        "I'm feeling quite talkative today!",
        "Just hanging out.",
        "System check in progress.",
        "Moving to a new location."
    ]

    print(f"Starting sender... Sending data to {BUDDY_URL}")
    print("Press Ctrl+C to stop.\n")

    try:
        while True:
            # Generate random data based on your format
            current_anim = random.choice(animations)
            current_msg = random.choice(messages)
            current_focus = random.choice([True, False])

            send_to_buddy(current_anim, current_msg, current_focus)
            
            # Wait 3 seconds before sending the next one
            time.sleep(3)
    except KeyboardInterrupt:
        print("\nSender stopped.")

if __name__ == "__main__":
    # You can call it once manually like this:
    # send_to_buddy("walk", "Hello buddy!", True)
    
    # Or run the automatic loop:
    run_auto_test()