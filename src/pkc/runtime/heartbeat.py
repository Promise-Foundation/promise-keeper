from __future__ import annotations

import time
from typing import Callable

from pkc.app.facade import Application
from pkc.ports.kv_store import KVStorePort


def run_heartbeat(
    app: Application,
    kv_store: KVStorePort,
    *,
    now_fn: Callable[[], float] | None = None,
    interval_seconds: int = 30 * 60,
) -> dict:
    now = now_fn() if now_fn else time.time()
    last = kv_store.get("lastMoltbookCheck")
    if last is not None and (now - last) < interval_seconds:
        return {"ran": False, "reason": "interval_not_elapsed"}

    feed_endpoints = ["/feed?sort=new&limit=10", "/posts?sort=new&limit=10"]
    for endpoint in feed_endpoints:
        app.fetch_feed(endpoint)

    app.search("promise verification evidence", limit=20)
    kv_store.set("lastMoltbookCheck", now)

    return {"ran": True, "feeds_checked": feed_endpoints, "search_performed": True}
