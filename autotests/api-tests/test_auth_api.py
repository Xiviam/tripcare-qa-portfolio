import pytest
from conftest import auth, login
from fastapi.testclient import TestClient


@pytest.mark.smoke
@pytest.mark.parametrize(
    ("email", "password", "role"),
    [
        ("customer@example.com", "Customer123!", "customer"),
        ("agent@example.com", "Agent123!", "support_agent"),
        ("admin@example.com", "Admin123!", "admin"),
    ],
)
def test_login_success_for_each_role(client: TestClient, email: str, password: str, role: str) -> None:
    token = login(client, email, password)
    response = client.get("/auth/me", headers=auth(token))
    assert response.status_code == 200
    assert response.json()["role"] == role


@pytest.mark.negative
@pytest.mark.parametrize(
    ("email", "password"),
    [
        ("customer@example.com", "bad"),
        ("missing@example.com", "Customer123!"),
        ("admin@example.com", ""),
    ],
)
def test_login_rejects_invalid_credentials(client: TestClient, email: str, password: str) -> None:
    response = client.post("/auth/login", json={"email": email, "password": password})
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "INVALID_CREDENTIALS"


@pytest.mark.contract
@pytest.mark.parametrize(
    "path", ["/auth/me", "/bookings/search?pnr=TC1001&last_name=Ivanov", "/admin/users", "/audit-log"]
)
def test_protected_endpoints_require_token(client: TestClient, path: str) -> None:
    response = client.get(path)
    assert response.status_code == 401


@pytest.mark.negative
def test_invalid_bearer_token_is_rejected(client: TestClient) -> None:
    response = client.get("/auth/me", headers={"Authorization": "Bearer broken.token.value"})
    assert response.status_code == 401
