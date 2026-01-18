import urllib.request
import json
import uuid

BASE_URL = "http://localhost:8004"

def register(username, email, password):
    url = f"{BASE_URL}/register"
    data = {
        "username": username,
        "email": email,
        "password": password
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode('utf-8'),
        headers={'Content-Type': 'application/json'}
    )
    try:
        with urllib.request.urlopen(req) as response:
            return response.status, json.loads(response.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()
    except Exception as e:
        return 500, str(e)

if __name__ == "__main__":
    u = f"user_{uuid.uuid4().hex[:8]}"
    e = f"{u}@test.com"
    print(f"Registering {u}...")
    status, body = register(u, e, "pass")
    print(f"Status: {status}")
    print(f"Body: {body}")
