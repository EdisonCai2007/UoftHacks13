import requests
from datetime import datetime

class APIClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.access_token = None

    def login(self, username, password):
        """Authenticates user and stores the access token."""
        try:
            response = requests.post(
                f"{self.base_url}/token",
                data={"username": username, "password": password},
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            response.raise_for_status()
            data = response.json()
            self.access_token = data["access_token"]
            return True, "Login successful"
        except requests.exceptions.RequestException as e:
            msg = "Connection failed"
            if hasattr(e, 'response') and e.response is not None:
                try:
                    detail = e.response.json().get('detail')
                    if detail:
                        msg = detail
                except:
                    pass
            return False, msg

    def upload_session(self, session_data):
        """Uploads session metrics to the backend."""
        if not self.access_token:
            return False, "Not authenticated"

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/sessions",
                json=session_data,
                headers=headers
            )
            response.raise_for_status()
            return True, response.json()
        except requests.exceptions.RequestException as e:
            return False, str(e)
