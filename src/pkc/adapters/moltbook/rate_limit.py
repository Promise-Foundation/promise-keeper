from __future__ import annotations

import time
from dataclasses import dataclass
from datetime import date

from pkc.adapters.moltbook.errors import MoltbookRateLimitError


@dataclass
class MoltbookRateLimitConfig:
    post_cooldown_seconds: int = 30 * 60
    comment_cooldown_seconds: int = 20
    comment_daily_limit: int = 50


class MoltbookRateLimiter:
    def __init__(self, config: MoltbookRateLimitConfig | None = None) -> None:
        self._config = config or MoltbookRateLimitConfig()
        self._last_post_at: float | None = None
        self._last_comment_at: float | None = None
        self._comment_day: date = date.today()
        self._comment_count: int = 0

    def check_post(self) -> None:
        now = time.time()
        if self._last_post_at is None:
            return
        elapsed = now - self._last_post_at
        if elapsed < self._config.post_cooldown_seconds:
            retry = int(self._config.post_cooldown_seconds - elapsed)
            raise MoltbookRateLimitError("POST_COOLDOWN", retry_after_seconds=retry)

    def record_post(self) -> None:
        self._last_post_at = time.time()

    def check_comment(self) -> None:
        now = time.time()
        today = date.today()
        if today != self._comment_day:
            self._comment_day = today
            self._comment_count = 0

        if self._comment_count >= self._config.comment_daily_limit:
            raise MoltbookRateLimitError("COMMENT_DAILY_CAP", retry_after_seconds=None)

        if self._last_comment_at is None:
            return
        elapsed = now - self._last_comment_at
        if elapsed < self._config.comment_cooldown_seconds:
            retry = int(self._config.comment_cooldown_seconds - elapsed)
            raise MoltbookRateLimitError("COMMENT_COOLDOWN", retry_after_seconds=retry)

    def record_comment(self) -> None:
        self._comment_count += 1
        self._last_comment_at = time.time()
