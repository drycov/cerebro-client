"""HTTP client for Cerebro OAuth + channel API."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class CerebroConfig:
    base_url: str
    username: str
    password: str
    timeout_seconds: float = 10.0


class CerebroClient:
    def __init__(self, config: CerebroConfig) -> None:
        import httpx

        self.config = config
        self._client = httpx.AsyncClient(
            base_url=config.base_url.rstrip("/"),
            timeout=config.timeout_seconds,
            follow_redirects=True,
        )
        self._token: str | None = None

    async def close(self) -> None:
        await self._client.aclose()

    async def authenticate(self) -> None:
        response = await self._client.post(
            "/oauth2/v1/auth/authenticate",
            json={"name": self.config.username, "password": self.config.password},
        )
        response.raise_for_status()
        data = response.json()
        self._token = data.get("access_token") or data.get("token")
        if not self._token:
            raise RuntimeError("Cerebro: нет access_token в ответе authenticate")

    async def request(self, method: str, path: str, **kwargs: Any) -> Any:
        if self._token is None:
            await self.authenticate()
        headers = dict(kwargs.pop("headers", {}) or {})
        headers["Authorization"] = f"Bearer {self._token}"
        response = await self._client.request(method, path, headers=headers, **kwargs)
        if response.status_code == 401:
            self._token = None
            await self.authenticate()
            headers["Authorization"] = f"Bearer {self._token}"
            response = await self._client.request(method, path, headers=headers, **kwargs)
        response.raise_for_status()
        return response.json()

    async def search_channels(self, offset: int = 0, limit: int = 1000) -> Any:
        return await self.request(
            "POST",
            "/api/v1/channels/search",
            json={
                "limit": limit,
                "offset": offset,
                "sort": "ASC",
                "sort_field": "name",
                "channel": {"composite_search": ""},
            },
        )

    async def get_channel(self, channel_id: int) -> dict[str, Any]:
        return await self.request("GET", f"/api/v1/channels/{channel_id}")
