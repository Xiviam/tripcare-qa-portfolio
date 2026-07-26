import pytest
from conftest import auth
from fastapi.testclient import TestClient


@pytest.mark.smoke
@pytest.mark.parametrize(
    ("pnr", "last_name"),
    [
        ("TC1001", "Ivanov"),
        ("TC1002", "Petrova"),
        ("TC1003", "Smirnov"),
        ("TC1004", "Kuznetsova"),
        ("TC1005", "Sokolov"),
        ("TC1006", "Popova"),
        ("TC1007", "Lebedev"),
        ("TC1008", "Kozlova"),
        ("TC1009", "Morozov"),
        ("TC1010", "Novikova"),
        ("TC1011", "Fedorov"),
        ("TC1012", "Mikhailova"),
    ],
)
def test_booking_search_valid_seed_data(
    client: TestClient, customer_token: str, pnr: str, last_name: str
) -> None:
    response = client.get(
        "/bookings/search", params={"pnr": pnr, "last_name": last_name}, headers=auth(customer_token)
    )
    assert response.status_code == 200
    assert response.json()[0]["pnr"] == pnr


@pytest.mark.negative
@pytest.mark.parametrize(
    ("pnr", "wrong_last_name"),
    [
        ("TC1001", "Petrova"),
        ("TC1002", "Ivanov"),
        ("TC1004", "Sokolov"),
        ("TC1008", "Fedorov"),
        ("TC1012", "Kozlova"),
    ],
)
def test_booking_search_requires_matching_last_name(
    client: TestClient, customer_token: str, pnr: str, wrong_last_name: str
) -> None:
    response = client.get(
        "/bookings/search", params={"pnr": pnr, "last_name": wrong_last_name}, headers=auth(customer_token)
    )
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.regression
@pytest.mark.parametrize("booking_id", [1, 2, 6, 12])
def test_booking_details_have_passengers_flights_and_status(
    client: TestClient, customer_token: str, booking_id: int
) -> None:
    response = client.get(f"/bookings/{booking_id}", headers=auth(customer_token))
    body = response.json()
    assert response.status_code == 200
    assert body["status"] in {"confirmed", "changed", "cancelled", "refund_pending", "refunded"}
    assert body["passengers"]
    assert body["flights"]


@pytest.mark.negative
def test_booking_details_unknown_id_returns_404(client: TestClient, customer_token: str) -> None:
    response = client.get("/bookings/99999", headers=auth(customer_token))
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "BOOKING_NOT_FOUND"
