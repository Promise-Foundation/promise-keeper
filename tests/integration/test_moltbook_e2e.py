import os

import pytest

from pkc.adapters.moltbook.client import MoltbookClientConfig, MoltbookHttpClient
from pkc.adapters.moltbook.platform import MoltbookPlatform


def _env(name: str) -> str | None:
    return os.getenv(name)


def _extract_status(payload: dict) -> str | None:
    if "status" in payload:
        return payload.get("status")
    data = payload.get("data")
    if isinstance(data, dict) and "status" in data:
        return data.get("status")
    return None


def _extract_agent(payload: dict) -> dict | None:
    if "agent" in payload and isinstance(payload.get("agent"), dict):
        return payload.get("agent")
    data = payload.get("data")
    if isinstance(data, dict) and isinstance(data.get("agent"), dict):
        return data.get("agent")
    return None


def test_moltbook_e2e_readonly() -> None:
    if _env("RUN_MOLTBOOK_E2E") != "1":
        pytest.skip("Set RUN_MOLTBOOK_E2E=1 to enable Moltbook E2E")

    api_key = _env("MOLTBOOK_API_KEY")
    if not api_key:
        pytest.skip("Set MOLTBOOK_API_KEY to enable Moltbook E2E")

    base_url = _env("MOLTBOOK_BASE_URL") or "https://www.moltbook.com/api/v1"
    if base_url != "https://www.moltbook.com/api/v1":
        pytest.skip("MOLTBOOK_BASE_URL must be https://www.moltbook.com/api/v1")

    try:
        client = MoltbookHttpClient(api_key, MoltbookClientConfig(base_url=base_url))
    except RuntimeError:
        pytest.skip("httpx not installed; install with uv sync --group moltbook")

    platform = MoltbookPlatform(client)

    status_payload = platform.get_agent_status()
    status = _extract_status(status_payload)
    assert status in {"pending_claim", "claimed"}

    profile_payload = platform.get_agent_profile()
    agent = _extract_agent(profile_payload)
    assert agent is None or isinstance(agent, dict)

    feed = platform.fetch_feed("/feed?sort=new&limit=1")
    assert isinstance(feed, list)
