from __future__ import annotations

import os
import sys
from collections.abc import Generator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

ROOT = Path(__file__).resolve().parents[1]
candidates = [
    ROOT.parent / "platform" / "services" / "api",
]
for candidate in candidates:
    if candidate.exists():
        sys.path.insert(0, str(candidate))
        break

os.environ["QA_BUG_MODE"] = "false"

from tripcare_api.database import Base, get_db  # noqa: E402
from tripcare_api.main import app  # noqa: E402
from tripcare_api.seed import seed_demo_data  # noqa: E402


@pytest.fixture()
def db_session() -> Generator[Session, None, None]:
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    with TestingSessionLocal() as db:
        seed_demo_data(db)
        yield db
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client(db_session: Session) -> Generator[TestClient, None, None]:
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def login(client: TestClient, email: str = "customer@example.com", password: str = "Customer123!") -> str:
    response = client.post("/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200
    return str(response.json()["access_token"])


def auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def customer_token(client: TestClient) -> str:
    return login(client)


@pytest.fixture()
def admin_token(client: TestClient) -> str:
    return login(client, "admin@example.com", "Admin123!")


@pytest.fixture()
def agent_token(client: TestClient) -> str:
    return login(client, "agent@example.com", "Agent123!")
