from dataclasses import dataclass


@dataclass(frozen=True)
class PromiseCard:
    promise_id: str
    promiser_id: str
    domain: str
    promise: str
    success_criteria: str
    evidence_plan: str
    assessment_window: str
    failure_modes: str = "kept / broken / inconclusive"
