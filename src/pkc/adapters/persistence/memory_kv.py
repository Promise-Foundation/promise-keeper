from __future__ import annotations

from pkc.ports.kv_store import KVStorePort


class InMemoryKVStore(KVStorePort):
    def __init__(self) -> None:
        self._store: dict[str, object] = {}

    def get(self, key: str):
        return self._store.get(key)

    def set(self, key: str, value) -> None:
        self._store[key] = value

    def clear(self) -> None:
        self._store.clear()
