"""
Amplitude Analytics Helper
Handles all Amplitude event tracking and querying
"""

import requests
import json
import os
from datetime import datetime, timedelta
from amplitude import Amplitude

# ========================
# CONFIGURATION
# ========================
AMPLITUDE_API_KEY = os.getenv("AMPLITUDE_API_KEY", "your-api-key-here")
AMPLITUDE_SECRET_KEY = os.getenv("AMPLITUDE_SECRET_KEY", "your-secret-key-here")

# Initialize Amplitude client
amplitude_client = Amplitude(AMPLITUDE_API_KEY)

# ========================
# EVENT TRACKING
# ========================

def track_distraction(user_id="default_user", session_id=None, metadata=None):
    """
    Track a distraction event when user looks away from screen.
    
    Args:
        user_id: Unique identifier for the user
        session_id: Current session ID
        metadata: Additional properties (e.g., duration, timestamp)
    """
    event_properties = {
        "session_id": session_id or generate_session_id(),
        "timestamp": datetime.now().isoformat()
    }
    
    if metadata:
        event_properties.update(metadata)
    
    try:
        amplitude_client.track(
            user_id=user_id,
            event_type="Distraction",
            event_properties=event_properties
        )
        print(f"📊 Tracked distraction event for user {user_id}")
        return True
    except Exception as e:
        print(f"❌ Failed to track distraction: {e}")
        return False


def track_session_start(user_id="default_user", session_id=None, tasks=None):
    """Track when a focus session starts."""
    event_properties = {
        "session_id": session_id or generate_session_id(),
        "tasks": tasks or [],
        "start_time": datetime.now().isoformat()
    }
    
    try:
        amplitude_client.track(
            user_id=user_id,
            event_type="Session_Start",
            event_properties=event_properties
        )
        print(f"📊 Tracked session start for user {user_id}")
        return True
    except Exception as e:
        print(f"❌ Failed to track session start: {e}")
        return False


def track_session_end(user_id="default_user", session_id=None, duration=None):
    """Track when a focus session ends."""
    event_properties = {
        "session_id": session_id or generate_session_id(),
        "end_time": datetime.now().isoformat(),
        "duration_seconds": duration
    }
    
    try:
        amplitude_client.track(
            user_id=user_id,
            event_type="Session_End",
            event_properties=event_properties
        )
        print(f"📊 Tracked session end for user {user_id}")
        return True
    except Exception as e:
        print(f"❌ Failed to track session end: {e}")
        return False


# ========================
# QUERYING ANALYTICS
# ========================

def get_distraction_count(user_id="default_user", session_id=None, hours=2):
    """
    Query Amplitude for distraction count in recent time period.
    
    Args:
        user_id: User to query for
        session_id: Specific session ID (optional)
        hours: How many hours back to query
    
    Returns:
        int: Number of distraction events
    """
    try:
        # Use Export API to get raw events
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=hours)
        
        url = "https://amplitude.com/api/2/export"
        
        params = {
            "start": start_time.strftime("%Y%m%dT%H"),
            "end": end_time.strftime("%Y%m%dT%H")
        }
        
        response = requests.get(
            url,
            params=params,
            auth=(AMPLITUDE_API_KEY, AMPLITUDE_SECRET_KEY),
            timeout=10
        )
        
        if response.status_code != 200:
            print(f"❌ Amplitude API error: {response.status_code}")
            return 0
        
        # Count distraction events
        distraction_count = 0
        for line in response.text.strip().split('\n'):
            if not line:
                continue
            try:
                event = json.loads(line)
                if event.get('event_type') == 'Distraction':
                    # Filter by session_id if provided
                    if session_id:
                        if event.get('event_properties', {}).get('session_id') == session_id:
                            distraction_count += 1
                    else:
                        distraction_count += 1
            except json.JSONDecodeError:
                continue
        
        print(f"📊 Found {distraction_count} distractions in last {hours} hours")
        return distraction_count
        
    except Exception as e:
        print(f"❌ Error querying Amplitude: {e}")
        return 0


def get_session_stats(session_id):
    """
    Get comprehensive stats for a specific session.
    
    Returns:
        dict: Session statistics including distractions, duration, etc.
    """
    try:
        distraction_count = get_distraction_count(session_id=session_id)
        
        return {
            "session_id": session_id,
            "distraction_count": distraction_count,
            "queried_at": datetime.now().isoformat()
        }
    except Exception as e:
        print(f"❌ Error getting session stats: {e}")
        return {"error": str(e)}


# ========================
# UTILITY FUNCTIONS
# ========================

def generate_session_id():
    """Generate a unique session ID based on timestamp."""
    return f"session_{int(datetime.now().timestamp())}"


def test_amplitude_connection():
    """Test if Amplitude API is properly configured."""
    try:
        # Try to track a test event
        amplitude_client.track(
            user_id="test_user",
            event_type="Test_Event",
            event_properties={"test": True}
        )
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
    print(f"\n📋 Session ID: {session_id}")
    
    # Track some events
    track_session_start(session_id=session_id, tasks=["Math homework", "Essay"])
    track_distraction(session_id=session_id, metadata={"duration": 15})
    track_distraction(session_id=session_id, metadata={"duration": 8})
    
    # Query stats
    print("\n📊 Querying stats...")
    count = get_distraction_count(hours=1)
    print(f"Total distractions: {count}")