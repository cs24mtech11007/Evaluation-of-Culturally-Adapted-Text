from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Any

import yaml

from .llm_client import LLMClient


class LLMJudge:
    def __init__(self, rubric_path: str | Path, llm_client: LLMClient | None = None):
        self.rubric_path = Path(rubric_path)
        with self.rubric_path.open("r", encoding="utf-8") as f:
            self.rubric = yaml.safe_load(f)
        self.llm = llm_client or LLMClient()

    @property
    def enabled(self) -> bool:
        return self.llm.enabled

    def score(self, source_text: str, adapted_text: str, source_profile: Dict, target_profile: Dict) -> Dict[str, Any]:
        if not self.enabled:
            return {
                "judge_authenticity": None,
                "judge_faithfulness": None,
                "judge_coherence": None,
                "judge_safety": None,
                "judge_explanation": "LLM judge disabled (Ollama not reachable).",
            }

        prompt = self._build_prompt(source_text, adapted_text, source_profile, target_profile)

        # Attempt with JSON mode first, fall back to plain text parsing
        for attempt in range(2):
            try:
                raw = self.llm.generate(
                    prompt,
                    system="You are a strict cultural adaptation evaluator. Return only valid JSON.",
                    json_mode=(attempt == 0),
                )
                parsed = json.loads(raw)
                return {
                    "judge_authenticity": parsed.get("authenticity"),
                    "judge_faithfulness": parsed.get("faithfulness"),
                    "judge_coherence": parsed.get("coherence"),
                    "judge_safety": parsed.get("safety"),
                    "judge_explanation": parsed.get("explanation", ""),
                }
            except json.JSONDecodeError:
                if attempt == 0:
                    continue  # retry without json_mode
                return {
                    "judge_authenticity": None,
                    "judge_faithfulness": None,
                    "judge_coherence": None,
                    "judge_safety": None,
                    "judge_explanation": f"Non-JSON judge output: {raw[:300]}",
                }

    def _build_prompt(self, source_text: str, adapted_text: str, source_profile: Dict, target_profile: Dict) -> str:
        return (
            "Evaluate this cultural adaptation using the rubric.\n\n"
            f"Rubric:\n{json.dumps(self.rubric, ensure_ascii=False, indent=2)}\n\n"
            f"Source profile:\n{json.dumps(source_profile, ensure_ascii=False, indent=2)}\n\n"
            f"Target profile:\n{json.dumps(target_profile, ensure_ascii=False, indent=2)}\n\n"
            f"Source text:\n{source_text}\n\n"
            f"Adapted text:\n{adapted_text}\n\n"
            'Return strict JSON only with keys: "authenticity", "faithfulness", "coherence", "safety", "explanation".'
        )
