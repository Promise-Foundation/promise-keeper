from dataclasses import dataclass


@dataclass(frozen=True)
class Assessment:
    assessment_id: str
    promise_id: str
    verdict: str
    evidence_cids: list[str]
