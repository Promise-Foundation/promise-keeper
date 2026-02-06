from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping

from pkc.domain.events import Event
from pkc.domain.models.promise import PromiseCard
from pkc.domain.services.promise_cards import create_promise_card, render_promise_card_markdown
from pkc.ports.event_log import EventLogPort
from pkc.ports.kv_store import KVStorePort
from pkc.ports.social_platform import SocialPlatformPort


@dataclass
class AppConfig:
    default_domain: str = "/coordination"


class Application:
    def __init__(
        self,
        *,
        social_platform: SocialPlatformPort,
        event_log: EventLogPort,
        kv_store: KVStorePort,
        config: AppConfig | None = None,
    ) -> None:
        self._social_platform = social_platform
        self._event_log = event_log
        self._kv_store = kv_store
        self._config = config or AppConfig()

    # Social platform primitives
    def create_post(self, submolt: str, title: str, content: str) -> str:
        return self._social_platform.create_post(submolt, title, content)

    def create_comment(
        self, post_id: str, content: str, parent_id: str | None = None
    ) -> str:
        return self._social_platform.create_comment(post_id, content, parent_id=parent_id)

    def create_post_idempotent(
        self, op_id: str, submolt: str, title: str, content: str
    ) -> str:
        key = f"op:post:{op_id}"
        existing = self._kv_store.get(key)
        if existing:
            return existing
        post_id = self.create_post(submolt, title, content)
        self._kv_store.set(key, post_id)
        return post_id

    def create_comment_idempotent(
        self, op_id: str, post_id: str, content: str, parent_id: str | None = None
    ) -> str:
        key = f"op:comment:{op_id}"
        existing = self._kv_store.get(key)
        if existing:
            return existing
        comment_id = self.create_comment(post_id, content, parent_id=parent_id)
        self._kv_store.set(key, comment_id)
        return comment_id

    def delete_post(self, post_id: str) -> None:
        self._social_platform.delete_post(post_id)

    def fetch_feed(self, endpoint: str) -> Iterable[Mapping[str, Any]]:
        return self._social_platform.fetch_feed(endpoint)

    def search(self, query: str, limit: int = 20) -> Iterable[Mapping[str, Any]]:
        return self._social_platform.search(query, limit=limit)

    # Protocol helpers
    def create_promise_card(
        self,
        *,
        promiser_id: str,
        promise: str,
        success_criteria: str,
        evidence_plan: str,
        assessment_window: str,
        domain: str | None = None,
    ) -> PromiseCard:
        return create_promise_card(
            promiser_id=promiser_id,
            domain=domain or self._config.default_domain,
            promise=promise,
            success_criteria=success_criteria,
            evidence_plan=evidence_plan,
            assessment_window=assessment_window,
        )

    def render_promise_card(self, card: PromiseCard) -> str:
        return render_promise_card_markdown(card)

    # Bridge helpers for Moltbook commands
    def handle_card_command(
        self,
        *,
        post_id: str,
        promiser_id: str,
        commitment_text: str,
        success_criteria: str,
        evidence_plan: str,
        assessment_window: str,
        domain: str | None = None,
    ) -> dict[str, str]:
        card = self.create_promise_card(
            promiser_id=promiser_id,
            promise=commitment_text,
            success_criteria=success_criteria,
            evidence_plan=evidence_plan,
            assessment_window=assessment_window,
            domain=domain,
        )
        rendered = self.render_promise_card(card)
        comment_id = self.create_comment(post_id, rendered)
        self._link_moltbook_to_cid(comment_id, card.promise_id)
        self._event_log.append(Event("PROMISE_CARD_CREATED", {"promise_id": card.promise_id}))
        return {"comment_id": comment_id, "promise_card_cid": card.promise_id}

    def handle_certify_command(self, promise_card_cid: str) -> None:
        self._event_log.append(Event("ASSESSMENT_REQUESTED", {"promise_id": promise_card_cid}))

    def handle_dispute_command(self, promise_card_cid: str) -> None:
        self._event_log.append(Event("DISPUTE_OPENED", {"promise_id": promise_card_cid}))

    def link_moltbook_to_cid(self, moltbook_id: str, cid: str) -> None:
        self._link_moltbook_to_cid(moltbook_id, cid)

    def get_cid_for_moltbook(self, moltbook_id: str) -> str | None:
        return self._kv_store.get(self._map_key(moltbook_id))

    def _link_moltbook_to_cid(self, moltbook_id: str, cid: str) -> None:
        self._kv_store.set(self._map_key(moltbook_id), cid)

    @staticmethod
    def _map_key(moltbook_id: str) -> str:
        return f"moltbook:{moltbook_id}:cid"
