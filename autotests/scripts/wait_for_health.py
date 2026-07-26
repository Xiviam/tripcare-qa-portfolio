from __future__ import annotations

import os
import time

import requests

base_url = os.getenv("BASE_URL", "http://127.0.0.1:8000")
deadline = time.time() + 60
while time.time() < deadline:
    try:
        response = requests.get(f"{base_url}/health", timeout=2)
        if response.status_code == 200 and response.json().get("status") == "ok":
            print("TripCare API is healthy")
            raise SystemExit(0)
    except requests.RequestException:
        pass
    time.sleep(1)
raise SystemExit("TripCare API did not become healthy")
