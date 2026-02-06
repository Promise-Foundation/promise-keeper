from dataclasses import dataclass


@dataclass(frozen=True)
class EvidenceEntry:
    evidence_id: str
    promise_id: str
    evidence_class: str
    artifact_cid: str | None = None
