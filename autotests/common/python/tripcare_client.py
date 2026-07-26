from __future__ import annotations

from typing import Any

import requests


class TripCareRemoteClient:
    def __init__(self, base_url: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()

    def login(self, email: str, password: str) -> str:
        response = self.session.post(
            f"{self.base_url}/auth/login", json={"email": email, "password": password}
        )
        response.raise_for_status()
        return str(response.json()["access_token"])

    def get(self, path: str, token: str | None = None, **kwargs: Any) -> requests.Response:
        headers = {"Authorization": f"Bearer {token}"} if token else None
        return self.session.get(f"{self.base_url}{path}", headers=headers, **kwargs)

    def post(self, path: str, token: str | None = None, **kwargs: Any) -> requests.Response:
        headers = {"Authorization": f"Bearer {token}"} if token else None
        return self.session.post(f"{self.base_url}{path}", headers=headers, **kwargs)

    def patch(self, path: str, token: str | None = None, **kwargs: Any) -> requests.Response:
        headers = {"Authorization": f"Bearer {token}"} if token else None
        return self.session.patch(f"{self.base_url}{path}", headers=headers, **kwargs)
