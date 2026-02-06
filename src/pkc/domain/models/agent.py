from dataclasses import dataclass


@dataclass(frozen=True)
class Agent:
    agent_id: str
    display_name: str
