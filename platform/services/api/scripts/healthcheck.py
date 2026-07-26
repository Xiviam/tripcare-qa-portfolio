import json
import urllib.request

with urllib.request.urlopen("http://localhost:8000/health", timeout=3) as response:
    body = json.loads(response.read().decode("utf8"))
    assert body["status"] == "ok"
