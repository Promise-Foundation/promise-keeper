from __future__ import annotations

from pkc.adapters.moltbook.memory_platform import InMemorySocialPlatform
from pkc.adapters.persistence.memory_event_log import InMemoryEventLog
from pkc.adapters.persistence.memory_kv import InMemoryKVStore
from pkc.app.facade import Application


def before_scenario(context, _scenario) -> None:
    context.social_platform = InMemorySocialPlatform()
    context.event_log = InMemoryEventLog()
    context.kv_store = InMemoryKVStore()
    context.app = Application(
        social_platform=context.social_platform,
        event_log=context.event_log,
        kv_store=context.kv_store,
    )

    # Simple container for step definitions to share state
    context.state = {}
