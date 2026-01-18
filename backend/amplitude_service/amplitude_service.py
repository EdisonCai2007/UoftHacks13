
"""
Amplitude Analytics Helper
Handles all Amplitude event tracking
"""

import os
from datetime import datetime
from amplitude import Amplitude, BaseEvent
import tkinter as tk
from tkinter import messagebox
from dotenv import load_dotenv

# Load .env file from parent directory
load_dotenv()

# ========================
# CONFIGURATION
# ========================
AMPLITUDE_API_KEY = os.getenv("AMPLITUDE_API_KEY")

if not AMPLITUDE_API_KEY:
    print("⚠️  WARNING: AMPLITUDE_API_KEY not found in environment variables")
    print("   Set it with: export AMPLITUDE_API_KEY=your_key_here")

# Initialize Amplitude client
amplitude_client = Amplitude(AMPLITUDE_API_KEY) if AMPLITUDE_API_KEY else None

# ========================
# EVENT TRACKING
# ========================

def track_tab_switch(user_id="default_user", session_id=None):
    """
    Track when user switches to a different tab/window.
    
    Args:
        user_id: Unique identifier for the user
        session_id: Current session ID
    """
    if not amplitude_client:
        print("❌ Amplitude not configured")
        return False
        
    event_properties = {
        "session_id": session_id or generate_session_id(),
        "timestamp": datetime.now().isoformat(),
    }
    
    try:
        event = BaseEvent(
            event_type="Tab_Switch",
            user_id=user_id,
            event_properties=event_properties
        )
        amplitude_client.track(event)
        return True
    except Exception as e:
        print(f"❌ Failed to track tab switch: {e}")
        return False


def track_look_away(user_id="default_user", session_id=None, duration_seconds=None):
    """
    Track when user looks away from screen and how long.
    
    Args:
        user_id: Unique identifier for the user
        session_id: Current session ID
        duration_seconds: How long they looked away (in seconds)
    """
    if not amplitude_client:
        print("❌ Amplitude not configured")
        return False
        
    event_properties = {
        "session_id": session_id or generate_session_id(),
        "timestamp": datetime.now().isoformat(),
        "duration_seconds": duration_seconds or 0
    }
    
    try:
        event = BaseEvent(
            event_type="Look_Away",
            user_id=user_id,
            event_properties=event_properties
        )
        amplitude_client.track(event)
        return True
    except Exception as e:
        print(f"❌ Failed to track look away: {e}")
        return False


def track_session_start(user_id="default_user", session_id=None, task=None, with_friends=None, with_food=None):
    """
    Track when a focus session starts.
    
    Args:
        user_id: Unique identifier for the user
        session_id: Current session ID
        task: User's task description
        with_friends: Whether user is with friends
        with_food: Whether user has food
    """
    if not amplitude_client:
        print("❌ Amplitude not configured")
        return False
        
    event_properties = {
        "session_id": session_id or generate_session_id(),
        "task": task or "",
        "start_time": datetime.now().isoformat(),
        "with_friends": with_friends or "",
        "with_food": with_food or ""
    }
    
    try:
        event = BaseEvent(
            event_type="Session_Start",
            user_id=user_id,
            event_properties=event_properties
        )
        amplitude_client.track(event)
        print(f"📊 Tracked session start for user {user_id}")
        return True
    except Exception as e:
        print(f"❌ Failed to track session start: {e}")
        return False


def track_session_end(user_id="default_user", session_id=None, duration=None, 
                      look_away_count=0, total_look_away_duration=0, tab_switch_count=0):
    """
    Track when a focus session ends and provide study assessment.
    
    Args:
        user_id: Unique identifier for the user
        session_id: Current session ID
        duration: Total session duration in seconds
        look_away_count: Number of times user looked away
        total_look_away_duration: Total time spent looking away in seconds
        tab_switch_count: Number of tab switches
    """
    if not amplitude_client:
        print("❌ Amplitude not configured")
        return False
        
    event_properties = {
        "session_id": session_id or generate_session_id(),
        "end_time": datetime.now().isoformat(),
        "duration_seconds": duration,
        "look_away_count": look_away_count,
        "total_look_away_duration": total_look_away_duration,
        "tab_switch_count": tab_switch_count
    }
    
    try:
        event = BaseEvent(
            event_type="Session_End",
            user_id=user_id,
            event_properties=event_properties
        )
        amplitude_client.track(event)
        # Flush to ensure event is sent before program exits
        amplitude_client.flush()
                
        print(f"📊 Tracked session end for user {user_id}")
        return True
    except Exception as e:
        print(f"❌ Failed to track session end: {e}")
        return False


# ========================
# UTILITY FUNCTIONS
# ========================

def generate_session_id():
    """Generate a unique session ID based on timestamp."""
    return f"session_{int(datetime.now().timestamp())}"


def test_amplitude_connection():
    """Test if Amplitude API is properly configured."""
    if not amplitude_client:
        print("❌ Amplitude not configured - set AMPLITUDE_API_KEY environment variable")
        return False
        
    try:
        # Try to track a test event
        event = BaseEvent(
            event_type="Test_Event",
            user_id="test_user",
            event_properties={"test": True}
        )
        amplitude_client.track(event)
        amplitude_client.flush()
        print("✅ Amplitude connection successful!")
        return True
    except Exception as e:
        print(f"❌ Amplitude connection failed: {e}")
        return False


# ========================
# EXAMPLE USAGE
# ========================

if __name__ == "__main__":
    print("Testing Amplitude Helper...")
    print("=" * 50)
    
    # Test connection
    test_amplitude_connection()
    
    # Generate session ID
    session_id = generate_session_id()
    device_id = "default_device"
    print(f"\n📋 Session ID: {session_id}")
    
    # Track some events
    track_session_start(
        session_id=session_id, 
        task="Math homework", 
        with_friends="No",
        with_food="Yes"
    )
    
    # User switches tab
    track_tab_switch(session_id=session_id)
    
    # User looks away for 15 seconds
    track_look_away(session_id=session_id, duration_seconds=15)
    
    # User switches tab again
    track_tab_switch(session_id=session_id)
    
    # User looks away for 45 seconds
    track_look_away(session_id=session_id, duration_seconds=45)
    
    track_session_end(session_id=session_id, duration=1800)
    
    print("\n✅ Events tracked! Check your Amplitude dashboard to see them.")