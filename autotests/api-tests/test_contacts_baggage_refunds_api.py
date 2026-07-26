import pytest
from conftest import auth
from fastapi.testclient import TestClient


@pytest.mark.regression
@pytest.mark.parametrize(
    ("booking_id", "email", "phone"),
    [
        (1, "ivanov.updated@example.test", "+79991234567"),
        (2, "petrova.updated@example.test", "79991234568"),
        (6, "popova.updated@example.test", "+79991234569"),
    ],
)
def test_contacts_update_valid_values(
    client: TestClient, customer_token: str, booking_id: int, email: str, phone: str
) -> None:
    response = client.patch(
        f"/bookings/{booking_id}/contacts",
        headers=auth(customer_token),
        json={"email": email, "phone": phone},
    )
    assert response.status_code == 200
    assert response.json()["contact_email"] == email


@pytest.mark.negative
@pytest.mark.parametrize(
    ("email", "phone", "code"),
    [
        ("bad-email", "+79991234567", "INVALID_EMAIL"),
        ("missing-at.example.test", "+79991234567", "INVALID_EMAIL"),
        ("valid@example.test", "12", "INVALID_PHONE"),
        ("valid@example.test", "+7abc", "INVALID_PHONE"),
        ("valid@example.test", "+7999123456789012", "INVALID_PHONE"),
        ("no-domain@", "79991234567", "INVALID_EMAIL"),
    ],
)
def test_contacts_reject_invalid_values(
    client: TestClient, customer_token: str, email: str, phone: str, code: str
) -> None:
    response = client.patch(
        "/bookings/1/contacts", headers=auth(customer_token), json={"email": email, "phone": phone}
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == code


@pytest.mark.parametrize(
    ("pieces", "weight", "expected"),
    [(1, 20, 3500), (1, 24, 3750), (2, 20, 8000), (2, 25, 8500), (3, 23, 12500), (3, 30, 14250)],
)
def test_baggage_price_decision_table(
    client: TestClient, customer_token: str, pieces: int, weight: int, expected: int
) -> None:
    response = client.post(
        "/bookings/1/baggage",
        headers=auth(customer_token),
        json={"passenger_name": "Passenger1 Ivanov", "pieces": pieces, "weight_kg": weight},
    )
    assert response.status_code == 201
    assert response.json()["price_cents"] == expected


@pytest.mark.negative
@pytest.mark.parametrize(
    "payload",
    [
        {"passenger_name": "P", "pieces": 1, "weight_kg": 20},
        {"passenger_name": "Passenger1 Ivanov", "pieces": 0, "weight_kg": 20},
        {"passenger_name": "Passenger1 Ivanov", "pieces": 6, "weight_kg": 20},
        {"passenger_name": "Passenger1 Ivanov", "pieces": 1, "weight_kg": 46},
    ],
)
def test_baggage_rejects_boundaries(client: TestClient, customer_token: str, payload: dict) -> None:
    response = client.post("/bookings/1/baggage", headers=auth(customer_token), json=payload)
    assert response.status_code == 422


@pytest.mark.regression
def test_refund_creation_success(client: TestClient, customer_token: str) -> None:
    response = client.post(
        "/bookings/1/refunds",
        headers=auth(customer_token),
        json={"reason": "Passenger cannot travel after schedule change"},
    )
    assert response.status_code == 201
    assert response.json()["status"] == "refund_pending"


@pytest.mark.negative
@pytest.mark.parametrize("booking_id", [4, 11])
def test_refund_duplicate_conflict(client: TestClient, customer_token: str, booking_id: int) -> None:
    response = client.post(
        f"/bookings/{booking_id}/refunds",
        headers=auth(customer_token),
        json={"reason": "Schedule changed and passenger cannot travel now"},
    )
    assert response.status_code == 409
