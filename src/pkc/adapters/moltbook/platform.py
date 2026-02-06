from __future__ import annotations

from typing import Any, Iterable, Mapping

from pkc.adapters.moltbook.client import MoltbookHttpClient
from pkc.adapters.moltbook.rate_limit import MoltbookRateLimiter
from pkc.ports.social_platform import SocialPlatformPort


class MoltbookPlatform(SocialPlatformPort):
    def __init__(
        self, client: MoltbookHttpClient, rate_limiter: MoltbookRateLimiter | None = None
    ) -> None:
        self._client = client
        self._rate_limiter = rate_limiter or MoltbookRateLimiter()

    def create_post(self, submolt: str, title: str, content: str) -> str:
        self._rate_limiter.check_post()
        response = self._client.request(
            "POST",
            "/posts",
            json={"submolt": submolt, "title": title, "content": content},
            send_auth=True,
        )
        self._rate_limiter.record_post()
        return response["json"].get("post_id", "")

    def create_comment(self, post_id: str, content: str, parent_id: str | None = None) -> str:
        self._rate_limiter.check_comment()
        payload: dict[str, Any] = {"content": content}
        if parent_id:
            payload["parent_id"] = parent_id
        response = self._client.request(
            "POST",
            f"/posts/{post_id}/comments",
            json=payload,
            send_auth=True,
        )
        self._rate_limiter.record_comment()
        return response["json"].get("comment_id", "")

    def delete_post(self, post_id: str) -> None:
        self._client.request("DELETE", f"/posts/{post_id}", send_auth=True)

    def fetch_feed(self, endpoint: str) -> Iterable[Mapping[str, Any]]:
        response = self._client.request("GET", endpoint, send_auth=True)
        return response["json"].get("posts", [])

    def search(self, query: str, limit: int = 20) -> Iterable[Mapping[str, Any]]:
        response = self._client.request(
            "GET",
            "/search",
            params={"q": query, "type": "all", "limit": limit},
            send_auth=True,
        )
        return response["json"].get("results", [])

    # Moltbook-specific API helpers
    def register_agent(self, name: str, description: str) -> dict:
        return self._client.request(
            "POST",
            "/agents/register",
            json={"name": name, "description": description},
            send_auth=False,
        )["json"]

    def get_agent_status(self) -> dict:
        return self._client.request("GET", "/agents/status", send_auth=True)["json"]

    def get_agent_profile(self) -> dict:
        return self._client.request("GET", "/agents/me", send_auth=True)["json"]

    def update_agent_profile(self, description: str) -> dict:
        return self._client.request(
            "PATCH", "/agents/me", json={"description": description}, send_auth=True
        )["json"]

    def heartbeat(self) -> str:
        response = self._client.request("GET", "/heartbeat.md", send_auth=False)
        return response["json"].get("text", "")
