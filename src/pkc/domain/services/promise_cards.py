from __future__ import annotations

from dataclasses import asdict
from typing import Any

from pkc.domain.models.promise import PromiseCard
from pkc.domain.services.canonical import canonical_json
from pkc.domain.services.ids import sha256_hex


def compute_promise_id(fields: dict[str, Any]) -> str:
    canonical = canonical_json(fields)
    return sha256_hex(canonical)


def create_promise_card(
    *,
    promiser_id: str,
    domain: str,
    promise: str,
    success_criteria: str,
    evidence_plan: str,
    assessment_window: str,
    failure_modes: str = "kept / broken / inconclusive",
) -> PromiseCard:
    data = {
        "promiser_id": promiser_id,
        "domain": domain,
        "promise": promise,
        "success_criteria": success_criteria,
        "evidence_plan": evidence_plan,
        "assessment_window": assessment_window,
        "failure_modes": failure_modes,
    }
    promise_id = compute_promise_id(data)
    return PromiseCard(promise_id=promise_id, **data)


def promise_card_to_dict(card: PromiseCard) -> dict[str, Any]:
    return asdict(card)


def render_promise_card_markdown(card: PromiseCard) -> str:
    return (
        "PROMISE CARD\n\n"
        f"From: {card.promiser_id}\n"
        f"Domain: {card.domain}\n"
        f"Promise: {card.promise}\n"
        f"Success Criteria: {card.success_criteria}\n"
        f"Evidence Plan: {card.evidence_plan}\n"
        f"Assessment Window: {card.assessment_window}\n"
        f"Failure Modes: {card.failure_modes}\n\n"
        f"promise_card_cid: {card.promise_id}\n"
    )
