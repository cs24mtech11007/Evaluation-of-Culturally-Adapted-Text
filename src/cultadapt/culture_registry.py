from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Any


class CultureRegistry:
    def __init__(self, config_path: str | Path):
        self.config_path = Path(config_path)
        with self.config_path.open("r", encoding="utf-8") as f:
            raw: Dict[str, Dict[str, Any]] = json.load(f)

        self.aliases: Dict[str, str] = raw.get("_aliases", {}) if isinstance(raw, dict) else {}
        self.profiles: Dict[str, Dict[str, Any]] = {
            k: v for k, v in raw.items() if not str(k).startswith("_")
        }

    def _resolve_key(self, culture_key: str) -> str:
        return self.aliases.get(culture_key, culture_key)

    def get(self, culture_key: str) -> Dict[str, Any]:
        resolved = self._resolve_key(culture_key)
        if resolved not in self.profiles:
            available = ", ".join(sorted(self.profiles.keys()))
            raise KeyError(f"Unknown culture '{culture_key}'. Available: {available}")
        return self.profiles[resolved]

    def format_profile(self, culture_key: str) -> str:
        p = self.get(culture_key)
        lines = [
            f"region: {p.get('region', '')}",
            f"languages: {', '.join(p.get('languages', []))}",
            f"names: {', '.join(p.get('names', []))}",
            f"foods: {', '.join(p.get('foods', []))}",
            f"festivals: {', '.join(p.get('festivals', []))}",
            f"places: {', '.join(p.get('places', []))}",
            f"social_context: {', '.join(p.get('social_context', []))}",
            f"tone_cues: {', '.join(p.get('tone_cues', []))}",
        ]
        return "\n".join(lines)
