from dataclasses import dataclass


@dataclass
class Settings:
    moltbook_base_url: str = "https://www.moltbook.com/api/v1"
