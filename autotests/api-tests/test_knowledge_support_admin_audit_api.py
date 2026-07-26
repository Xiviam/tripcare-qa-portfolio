import pytest
from conftest import auth
from fastapi.testclient import TestClient
from jsonschema import validate


@pytest.mark.contract
@pytest.mark.parametrize("query", ["baggage", "BAGGAGE", "refund", "mobile", "support"])
def test_knowledge_base_search_queries(client: TestClient, query: str) -> None:
    response = client.get("/knowledge-base", params={"q": query})
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.contract
def test_knowledge_base_article_schema(client: TestClient) -> None:
    response = client.get("/knowledge-base", params={"q": "baggage"})
    schema = {"type": "object", "required": ["id", "title", "body", "tags"]}
    validate(response.json()[0], schema)


@pytest.mark.regression
@pytest.mark.parametrize("severity", ["low", "medium", "high"])
def test_support_ticket_creation_by_severity(client: TestClient, customer_token: str, severity: str) -> None:
    response = client.post(
        "/support/tickets",
        headers=auth(customer_token),
        json={
            "booking_id": 1,
            "subject": f"Severity {severity}",
            "message": "Please check booking options.",
            "severity": severity,
        },
    )
    assert response.status_code == 201
    assert response.json()["severity"] == severity


@pytest.mark.negative
def test_support_ticket_rejects_empty_message(client: TestClient, customer_token: str) -> None:
    response = client.post(
        "/support/tickets",
        headers=auth(customer_token),
        json={"booking_id": 1, "subject": "Empty", "message": "", "severity": "medium"},
    )
    assert response.status_code == 422


@pytest.mark.regression
def test_support_ticket_pagination_respects_page_size(client: TestClient, customer_token: str) -> None:
    response = client.get(
        "/support/tickets", params={"page": 1, "page_size": 2}, headers=auth(customer_token)
    )
    assert response.status_code == 200
    assert len(response.json()) <= 2


@pytest.mark.parametrize(
    ("email", "password", "expected"),
    [
        ("customer@example.com", "Customer123!", 403),
        ("agent@example.com", "Agent123!", 403),
        ("admin@example.com", "Admin123!", 200),
    ],
)
def test_admin_users_role_matrix(client: TestClient, email: str, password: str, expected: int) -> None:
    from conftest import login

    token = login(client, email, password)
    response = client.get("/admin/users", headers=auth(token))
    assert response.status_code == expected


@pytest.mark.parametrize(
    ("email", "password", "expected"),
    [
        ("customer@example.com", "Customer123!", 403),
        ("agent@example.com", "Agent123!", 200),
        ("admin@example.com", "Admin123!", 200),
    ],
)
def test_audit_log_role_matrix(client: TestClient, email: str, password: str, expected: int) -> None:
    from conftest import login

    token = login(client, email, password)
    response = client.get("/audit-log", headers=auth(token))
    assert response.status_code == expected
