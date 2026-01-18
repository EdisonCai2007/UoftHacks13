import os
import sys
import time
import json
from tkinter import messagebox
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
import tkinter as tk


load_dotenv()

AMPLITUDE_API_KEY = os.getenv("AMPLITUDE_API_KEY")
AMPLITUDE_SECRET_KEY = os.getenv("AMPLITUDE_SECRET_KEY")
WEBHOOK_LINK = "http://localhost:5678/webhook/4819f694-a4de-48f9-a8ee-9d0ba9e17dd8"

AMPLITUDE_BASE = "https://amplitude.com/api/2/events/segmentation"

EVENTS = [
    "Session_Start",
    "Session_End",
    "Tab_Switch",
    "Look_Away"
]

# ----------------------------
# Amplitude data
# ----------------------------

def get_date_range():
    yesterday = datetime.utcnow() - timedelta(days=1)
    return yesterday.strftime("%Y%m%d"), yesterday.strftime("%Y%m%d")

def fetch_single_event_count(event_name, start, end):
    params = {
        "e": json.dumps({"event_type": event_name}),
        "start": start,
        "end": end,
        "m": "totals"  # 👈 THIS IS THE KEY
    }

    r = requests.get(
        AMPLITUDE_BASE,
        params=params,
        auth=(AMPLITUDE_API_KEY, AMPLITUDE_SECRET_KEY),
        timeout=30
    )

    r.raise_for_status()
    data = r.json()

    try:
        return sum(data["data"]["series"][0])
    except (KeyError, IndexError, TypeError):
        return 0


def fetch_event_counts():
    start, end = get_date_range()
    counts = {}

    for event in EVENTS:
        counts[event] = fetch_single_event_count(event, start, end)
        time.sleep(0.2)  # avoid Amplitude rate limits

    return counts

# ----------------------------
# AI insight
# ----------------------------

def send_to_webhook(summary, human_focus_rating):

    data = {
        "counts": summary,
        "prompt": f"""
            You are analyzing focus behavior.

            Return ONLY valid JSON with this exact schema:

            {{
            "ai_focus_rating": number,  // integer 1-10
            "sensitivity_judgement": "too sensitive" | "just right" | "not sensitive enough",
            "reason": string,
            "recommended_track_look_away": number
            }}

            Rules:
            - Compare ai_focus_rating to human focus rating = {human_focus_rating}
            - If AI rating << human rating → system is too sensitive
            - If close (±1) → just right
            - If AI rating >> human rating → not sensitive enough
            - recommended_track_look_away must be higher if not sensitive enough, lower if too sensitive
            """
    }

    response = requests.post(WEBHOOK_LINK, json=data, timeout=30)
    response.raise_for_status()

    return response.json()

# ----------------------------
# Main
# ----------------------------

def main():
    # Get human focus rating from command line argument
    if len(sys.argv) > 1:
        try:
            human_focus_rating = int(sys.argv[1])
        except ValueError:
            print("Error: Invalid focus rating. Using default value of 5.")
            human_focus_rating = 5
    else:
        print("No focus rating provided. Using default value of 5.")
        human_focus_rating = 5
    
    print(f"Fetching Amplitude data with human focus rating: {human_focus_rating}")
    
    counts = fetch_event_counts()

    insight = send_to_webhook(counts, human_focus_rating)
    recommended_value = insight.get('recommended_track_look_away')
    
    # Write to a JSON file
    config_file = os.path.join(os.path.dirname(__file__), '..', 'config.json')
    
    # Read existing config
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        config = {}
    
    # Update MIN_LOOK_AWAY_DURATION
    config['MIN_LOOK_AWAY_DURATION'] = recommended_value
    config['last_updated'] = datetime.utcnow().isoformat()
    
    # Write back
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"✅ Updated MIN_LOOK_AWAY_DURATION to {recommended_value}")

if __name__ == "__main__":
    main()