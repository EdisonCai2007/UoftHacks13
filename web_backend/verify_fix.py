import urllib.request
import json
import uuid

BASE_URL = "http://localhost:8002"

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
        return e.code, json.loads(e.read().decode())
    except urllib.error.URLError as e:
        return 500, {"detail": str(e)}

def text_fix():
    with open("result.txt", "w") as f:
        f.write("Starting verification...\n")
        
        # 1. Register new user
        u1 = f"user_{uuid.uuid4().hex[:8]}"
        e1 = f"{u1}@example.com"
        pwd = "password123"
        
        f.write(f"Registering {u1} with {e1}...\n")
        status, data = register(u1, e1, pwd)
        if status == 200:
            f.write("PASS: Registration successful\n")
        else:
            f.write(f"FAIL: Registration failed: {status} {data}\n")

        # 2. Register same email, different user
        u2 = f"user_{uuid.uuid4().hex[:8]}"
        f.write(f"Registering {u2} with EXISTING email {e1}...\n")
        status, data = register(u2, e1, pwd)
        if status == 400 and "Email already registered" in data.get("detail", ""):
            f.write("PASS: Correctly rejected duplicate email\n")
        else:
            f.write(f"FAIL: Unexpected response for duplicate email: {status} {data}\n")

        # 3. Register same user, different email
        e2 = f"{u2}@example.com"
        f.write(f"Registering EXISTING user {u1} with new email {e2}...\n")
        status, data = register(u1, e2, pwd)
        if status == 400 and "Username already registered" in data.get("detail", ""):
            f.write("PASS: Correctly rejected duplicate username\n")
        else:
            f.write(f"FAIL: Unexpected response for duplicate username: {status} {data}\n")

if __name__ == "__main__":
    text_fix()
