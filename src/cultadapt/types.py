from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Dict, Optional


@dataclass
class AdaptationItem:
    id: str
    text: str
    source_culture: str
    target_culture: str
    genre: str = "general"
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class AdaptationResult:
    id: str
    source_text: str
    adapted_text: str
    source_culture: str
    target_culture: str
    genre: str
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
