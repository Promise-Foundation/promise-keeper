from __future__ import annotations

from pkc.domain.events import Event
from pkc.ports.event_log import EventLogPort


class InMemoryEventLog(EventLogPort):
    def __init__(self) -> None:
        self.events: list[Event] = []

    def append(self, event: Event) -> None:
        self.events.append(event)

    def clear(self) -> None:
        self.events.clear()
