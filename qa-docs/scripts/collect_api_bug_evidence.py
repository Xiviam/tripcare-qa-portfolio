from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLATFORM_API = ROOT.parent / "platform" / "services" / "api"
sys.path.insert(0, str(PLATFORM_API))
os.environ["QA_BUG_MODE"] = "true"

from fastapi.testclient import TestClient  # noqa: E402

from tripcare_api.main import app  # noqa: E402

OUT = ROOT / "evidence" / "logs"
OUT.mkdir(parents=True, exist_ok=True)


def dump(name: str, payload: dict) -> None:
    (OUT / f"{name}-response.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False),
        encoding="utf8",
    )


with TestClient(app) as client:
    token = client.post(
        "/auth/login",
        json={"email": "customer@example.com", "password": "Customer123!"},
    ).json()["access_token"]
    admin_token = client.post(
        "/auth/login",
        json={"email": "admin@example.com", "password": "Admin123!"},
    ).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    dump("BUG-001", client.patch("/bookings/1/contacts", headers=headers, json={"email": "bad-email", "phone": "+79991234567"}).json())
    dump("BUG-002", client.post("/bookings/1/baggage", headers=headers, json={"passenger_name": "Passenger1 Ivanov", "pieces": 2, "weight_kg": 25}).json())
    dump("BUG-003", client.post("/bookings/4/refunds", headers=headers, json={"reason": "Schedule changed and passenger cannot travel now"}).json())
    dump("BUG-004", client.post("/support/tickets", headers=headers, json={"booking_id": 1, "subject": "Question", "message": "", "severity": "medium"}).json())
    dump("BUG-005", {"query": "BAGGAGE", "results": client.get("/knowledge-base", params={"q": "BAGGAGE"}).json()})
    dump("BUG-006", client.get("/admin/users", headers=headers).json())
    client.post("/bookings/2/baggage", headers=headers, json={"passenger_name": "Passenger1 Petrova", "pieces": 1, "weight_kg": 20})
    dump("BUG-007", {"audit": client.get("/audit-log", headers=admin_headers).json()[:10]})
    dump("BUG-008", client.get("/bookings/search", params={"pnr": "TC1001", "last_name": "Petrova"}, headers=headers).json())
    dump("BUG-009", client.patch("/bookings/1/contacts", headers=headers, json={"email": "ok@example.test", "phone": "12"}).json())
    for i in range(3):
        client.post("/support/tickets", headers=headers, json={"booking_id": 1, "subject": f"Page size {i}", "message": "Pagination evidence message", "severity": "low"})
    dump("BUG-010", client.get("/support/tickets", params={"page": 1, "page_size": 1}, headers=headers).json())

print("API bug evidence saved")
