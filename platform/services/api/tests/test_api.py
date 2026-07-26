from fastapi.testclient import TestClient

from .conftest import auth_header


def test_health_returns_ok(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "ok"}


def test_login_returns_token(client: TestClient) -> None:
    response = client.post(
        "/auth/login",
        json={"email": "customer@example.com", "password": "Customer123!"},
    )
    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"


def test_login_rejects_wrong_password(client: TestClient) -> None:
    response = client.post(
        "/auth/login",
        json={"email": "customer@example.com", "password": "wrong"},
    )
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "INVALID_CREDENTIALS"


def test_me_returns_current_user(client: TestClient) -> None:
    response = client.get("/auth/me", headers=auth_header(client))
    assert response.status_code == 200
    assert response.json()["role"] == "customer"


def test_booking_search_requires_auth(client: TestClient) -> None:
    response = client.get("/bookings/search", params={"pnr": "TC1001", "last_name": "Ivanov"})
    assert response.status_code == 401


def test_booking_search_uses_pnr_and_last_name(client: TestClient) -> None:
    headers = auth_header(client)
    found = client.get(
        "/bookings/search",
        params={"pnr": "tc1001", "last_name": "ivanov"},
        headers=headers,
    )
    missing = client.get(
        "/bookings/search",
        params={"pnr": "TC1001", "last_name": "Petrova"},
        headers=headers,
    )
    assert found.status_code == 200
    assert len(found.json()) == 1
    assert missing.status_code == 200
    assert missing.json() == []


def test_booking_details_include_nested_entities(client: TestClient) -> None:
    headers = auth_header(client)
    search = client.get(
        "/bookings/search",
        params={"pnr": "TC1002", "last_name": "Petrova"},
        headers=headers,
    )
    booking_id = search.json()[0]["id"]
    response = client.get(f"/bookings/{booking_id}", headers=headers)
    data = response.json()
    assert response.status_code == 200
    assert data["pnr"] == "TC1002"
    assert len(data["passengers"]) == 2
    assert data["flights"][0]["flight_no"].startswith("TC")


def test_booking_details_return_404_for_unknown_id(client: TestClient) -> None:
    response = client.get("/bookings/99999", headers=auth_header(client))
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "BOOKING_NOT_FOUND"


def test_contacts_update_success(client: TestClient) -> None:
    headers = auth_header(client)
    booking = client.get(
        "/bookings/search",
        params={"pnr": "TC1001", "last_name": "Ivanov"},
        headers=headers,
    ).json()[0]
    response = client.patch(
        f"/bookings/{booking['id']}/contacts",
        headers=headers,
        json={"email": "new.ivanov@example.test", "phone": "+79991234567"},
    )
    assert response.status_code == 200
    assert response.json()["contact_email"] == "new.ivanov@example.test"


def test_contacts_reject_invalid_email(client: TestClient) -> None:
    headers = auth_header(client)
    response = client.patch(
        "/bookings/1/contacts",
        headers=headers,
        json={"email": "bad-email", "phone": "+79991234567"},
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "INVALID_EMAIL"


def test_contacts_reject_invalid_phone(client: TestClient) -> None:
    headers = auth_header(client)
    response = client.patch(
        "/bookings/1/contacts",
        headers=headers,
        json={"email": "valid@example.test", "phone": "12"},
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "INVALID_PHONE"


def test_baggage_price_for_first_piece(client: TestClient) -> None:
    response = client.post(
        "/bookings/1/baggage",
        headers=auth_header(client),
        json={"passenger_name": "Passenger1 Ivanov", "pieces": 1, "weight_kg": 20},
    )
    assert response.status_code == 201
    assert response.json()["price_cents"] == 3500


def test_baggage_price_for_extra_piece_and_overweight(client: TestClient) -> None:
    response = client.post(
        "/bookings/1/baggage",
        headers=auth_header(client),
        json={"passenger_name": "Passenger1 Ivanov", "pieces": 2, "weight_kg": 25},
    )
    assert response.status_code == 201
    assert response.json()["price_cents"] == 8500


def test_refund_creation_conflict_for_existing_refund(client: TestClient) -> None:
    headers = auth_header(client)
    response = client.post(
        "/bookings/4/refunds",
        headers=headers,
        json={"reason": "Schedule changed and passenger cannot travel now"},
    )
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "REFUND_ALREADY_EXISTS"


def test_refund_creation_success(client: TestClient) -> None:
    response = client.post(
        "/bookings/1/refunds",
        headers=auth_header(client),
        json={"reason": "Passenger cannot travel after schedule change"},
    )
    assert response.status_code == 201
    assert response.json()["status"] == "refund_pending"


def test_knowledge_base_search_is_case_insensitive(client: TestClient) -> None:
    response = client.get("/knowledge-base", params={"q": "BAGGAGE"})
    assert response.status_code == 200
    assert response.json()[0]["title"] == "How to add baggage"


def test_ticket_requires_message(client: TestClient) -> None:
    response = client.post(
        "/support/tickets",
        headers=auth_header(client),
        json={"booking_id": 1, "subject": "Question", "message": "", "severity": "medium"},
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "EMPTY_MESSAGE"


def test_ticket_creation_and_pagination(client: TestClient) -> None:
    headers = auth_header(client)
    created = client.post(
        "/support/tickets",
        headers=headers,
        json={
            "booking_id": 1,
            "subject": "Seat request",
            "message": "Please check if window seats are available.",
            "severity": "low",
        },
    )
    assert created.status_code == 201
    listed = client.get("/support/tickets", params={"page": 1, "page_size": 2}, headers=headers)
    assert listed.status_code == 200
    assert len(listed.json()) <= 2


def test_customer_cannot_list_admin_users(client: TestClient) -> None:
    response = client.get("/admin/users", headers=auth_header(client))
    assert response.status_code == 403


def test_admin_can_list_users(client: TestClient) -> None:
    headers = auth_header(client, "admin@example.com", "Admin123!")
    response = client.get("/admin/users", headers=headers)
    assert response.status_code == 200
    assert {user["role"] for user in response.json()} == {"customer", "support_agent", "admin"}


def test_support_agent_can_read_audit_log(client: TestClient) -> None:
    headers = auth_header(client, "agent@example.com", "Agent123!")
    response = client.get("/audit-log", headers=headers)
    assert response.status_code == 200
    assert response.json()[0]["action"] == "seed_demo_data"
