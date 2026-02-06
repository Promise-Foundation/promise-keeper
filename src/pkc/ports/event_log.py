# ruff: noqa: I001
from typing import Protocol

from pkc.domain.events import Event

class EventLogPort(Protocol):
    def append(self, event: Event) -> None: ...
