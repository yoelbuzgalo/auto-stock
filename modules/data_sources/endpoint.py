from dataclasses import dataclass, field
from typing import Dict, Any


@dataclass(slots=True)
class Endpoint:
    base_url: str
    path: str
    method: str
    headers: Dict[str, str] = field(default_factory=dict)
    params: Dict[str, Any] = field(default_factory=dict)
    timeout: int = 10

    @property
    def url(self) -> str:
        return f"{self.base_url.rstrip('/')}/{self.path.lstrip('/')}"