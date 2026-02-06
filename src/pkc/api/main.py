from __future__ import annotations

import os
from typing import Any, Dict, Tuple

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field

from pkc.domain.services.canonical import canonical_json
from pkc.domain.services.ids import sha256_hex
from pkc.domain.services.promise_cards import (
    create_promise_card,
    promise_card_to_dict,
    render_promise_card_markdown,
)

APP_VERSION = "0.1.0"
DEFAULT_DOMAIN = os.getenv("PK_DEFAULT_DOMAIN", "/coordination")

app = FastAPI(title="Promise Keeper API", version=APP_VERSION)
security = HTTPBearer(auto_error=False)


# -------------------------
# In-memory stores (Phase 0)
# -------------------------
PROMISE_CARDS: Dict[str, Dict[str, Any]] = {}
EVIDENCE_ENTRIES: Dict[str, Dict[str, Any]] = {}
ASSESSMENTS: Dict[str, Dict[str, Any]] = {}


# -------------------------
# Auth
# -------------------------

def require_api_key(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> None:
    expected = os.getenv("PK_API_KEY")
    if not expected:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="PK_API_KEY not configured",
        )
    if not credentials or credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    if credentials.credentials != expected:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")


# -------------------------
# Models
# -------------------------

class PromiseCardCreate(BaseModel):
    promiser_id: str
    domain: str | None = None
    promise: str
    success_criteria: str
    evidence_plan: str
    assessment_window: str
    failure_modes: str | None = None


class EvidenceCreate(BaseModel):
    promise_id: str
    evidence_class: str
    artifact_cid: str | None = None


class AssessmentCreate(BaseModel):
    promise_id: str
    verdict: str
    evidence_cids: list[str] = Field(default_factory=list)


# -------------------------
# Helpers
# -------------------------

def _compute_cid(fields: Dict[str, Any]) -> str:
    return sha256_hex(canonical_json(fields))


def _promise_canonical_fields(card: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "promiser_id": card["promiser_id"],
        "domain": card["domain"],
        "promise": card["promise"],
        "success_criteria": card["success_criteria"],
        "evidence_plan": card["evidence_plan"],
        "assessment_window": card["assessment_window"],
        "failure_modes": card["failure_modes"],
    }


def _find_object(cid: str) -> Tuple[str, Dict[str, Any]] | None:
    if cid in PROMISE_CARDS:
        return "promise_card", PROMISE_CARDS[cid]
    if cid in EVIDENCE_ENTRIES:
        return "evidence", EVIDENCE_ENTRIES[cid]
    if cid in ASSESSMENTS:
        return "assessment", ASSESSMENTS[cid]
    return None


# -------------------------
# Routes
# -------------------------

@app.get("/health")
def health() -> Dict[str, bool]:
    return {"ok": True}


@app.post("/cards", dependencies=[Depends(require_api_key)])
def create_card(payload: PromiseCardCreate) -> Dict[str, Any]:
    card = create_promise_card(
        promiser_id=payload.promiser_id,
        domain=payload.domain or DEFAULT_DOMAIN,
        promise=payload.promise,
        success_criteria=payload.success_criteria,
        evidence_plan=payload.evidence_plan,
        assessment_window=payload.assessment_window,
        failure_modes=payload.failure_modes or "kept / broken / inconclusive",
    )
    card_dict = promise_card_to_dict(card)
    canonical = _promise_canonical_fields(card_dict)
    PROMISE_CARDS[card.promise_id] = {"canonical": canonical, "data": card_dict}
    rendered = render_promise_card_markdown(card)
    return {
        "promise_card_cid": card.promise_id,
        "promise_card": card_dict,
        "promise_card_markdown": rendered,
    }


@app.post("/evidence", dependencies=[Depends(require_api_key)])
def create_evidence(payload: EvidenceCreate) -> Dict[str, Any]:
    canonical = {
        "promise_id": payload.promise_id,
        "evidence_class": payload.evidence_class,
        "artifact_cid": payload.artifact_cid,
    }
    evidence_id = _compute_cid(canonical)
    EVIDENCE_ENTRIES[evidence_id] = {
        "canonical": canonical,
        "data": {**canonical, "evidence_id": evidence_id},
    }
    return {"evidence_id": evidence_id, "evidence": EVIDENCE_ENTRIES[evidence_id]["data"]}


@app.post("/assessments", dependencies=[Depends(require_api_key)])
def create_assessment(payload: AssessmentCreate) -> Dict[str, Any]:
    canonical = {
        "promise_id": payload.promise_id,
        "verdict": payload.verdict,
        "evidence_cids": payload.evidence_cids,
    }
    assessment_id = _compute_cid(canonical)
    ASSESSMENTS[assessment_id] = {
        "canonical": canonical,
        "data": {**canonical, "assessment_id": assessment_id},
    }
    return {"assessment_id": assessment_id, "assessment": ASSESSMENTS[assessment_id]["data"]}


@app.get("/verify/{cid}")
def verify_cid(cid: str) -> Dict[str, Any]:
    result = _find_object(cid)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="CID not found")
    object_type, obj = result
    canonical = obj["canonical"]
    computed = _compute_cid(canonical)
    return {
        "cid": cid,
        "computed_cid": computed,
        "matches": computed == cid,
        "object_type": object_type,
        "canonical": canonical,
    }


@app.get("/resolve/{cid}")
def resolve_cid(cid: str) -> Dict[str, Any]:
    result = _find_object(cid)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="CID not found")
    object_type, obj = result
    return {"cid": cid, "object_type": object_type, "data": obj["data"]}
