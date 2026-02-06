from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from urllib.parse import urlparse

try:
    import httpx
except Exception:  # pragma: no cover - optional dependency
    httpx = None

from pkc.adapters.moltbook.errors import MoltbookRateLimitError, MoltbookSecurityError


@dataclass(frozen=True)
class MoltbookClientConfig:
    base_url: str = "https://www.moltbook.com/api/v1"
    timeout_seconds: float = 10.0


class MoltbookHttpClient:
    def __init__(self, api_key: str, config: MoltbookClientConfig | None = None) -> None:
        if httpx is None:
            raise RuntimeError("httpx is required for MoltbookHttpClient")
        self._api_key = api_key
        self._config = config or MoltbookClientConfig()
        self._client = httpx.Client(
            base_url=self._config.base_url,
            timeout=self._config.timeout_seconds,
            follow_redirects=False,
        )

    def request(
        self,
        method: str,
        path: str,
        *,
        json: dict | None = None,
        params: dict | None = None,
        send_auth: bool = True,
    ) -> dict[str, Any]:
        url = self._build_url(path)
        headers: dict[str, str] = {}
        if send_auth:
            headers["Authorization"] = f"Bearer {self._api_key}"
            self._validate_allowlist(url)

        response = self._client.request(method, url, json=json, params=params, headers=headers)
        if send_auth and 300 <= response.status_code < 400:
            raise MoltbookSecurityError("REDIRECT_WITH_AUTH_DETECTED")
        if response.status_code == 429:
            retry_after = response.headers.get("Retry-After")
            retry_seconds = int(retry_after) if retry_after and retry_after.isdigit() else None
            raise MoltbookRateLimitError("RATE_LIMITED", retry_after_seconds=retry_seconds)

        return {
            "status_code": response.status_code,
            "json": response.json() if response.content else {},
        }

    def _build_url(self, path: str) -> str:
        if path.startswith("http://") or path.startswith("https://"):
            return path
        if not path.startswith("/"):
            path = f"/{path}"
        return f"{self._config.base_url}{path}"

    def _validate_allowlist(self, url: str) -> None:
        parsed = urlparse(url)
        if parsed.hostname != "www.moltbook.com":
            raise MoltbookSecurityError("API_KEY_EXFILTRATION_BLOCKED")
        if not parsed.path.startswith("/api/v1/"):
            raise MoltbookSecurityError("API_KEY_EXFILTRATION_BLOCKED")
