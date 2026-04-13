from __future__ import annotations

import re
from pathlib import Path

from .culture_registry import CultureRegistry
from .llm_client import LLMClient
from .prompts import load_template, render_template
from .types import AdaptationItem, AdaptationResult


class CulturalAdapter:
    def __init__(
        self,
        culture_config: str | Path,
        prompt_template: str | Path,
        llm_client: LLMClient | None = None,
    ):
        self.registry = CultureRegistry(culture_config)
        self.template = load_template(prompt_template)
        self.llm = llm_client or LLMClient()

    def adapt(self, item: AdaptationItem) -> AdaptationResult:
        source_profile = self.registry.format_profile(item.source_culture)
        target_profile = self.registry.format_profile(item.target_culture)
        prompt = render_template(
            self.template,
            source_profile=source_profile,
            target_profile=target_profile,
            genre=item.genre,
            text=item.text,
        )

        if self.llm.enabled:
            adapted = self.llm.generate(prompt)
        else:
            adapted = self._fallback_rewrite(item)

        return AdaptationResult(
            id=item.id,
            source_text=item.text,
            adapted_text=adapted,
            source_culture=item.source_culture,
            target_culture=item.target_culture,
            genre=item.genre,
            metadata=item.metadata,
        )

    def _fallback_rewrite(self, item: AdaptationItem) -> str:
        src = self.registry.get(item.source_culture)
        tgt = self.registry.get(item.target_culture)
        text = item.text

        text = self._replace_any(text, src.get("places", []), tgt.get("places", []))
        text = self._replace_any(text, src.get("foods", []), tgt.get("foods", []))
        text = self._replace_any(text, src.get("festivals", []), tgt.get("festivals", []))
        text = self._replace_any(text, src.get("names", []), tgt.get("names", []))

        # Add a contextual cue if no obvious substitutions occurred
        if text == item.text and tgt.get("social_context"):
            text = f"{text} The setting reflects {tgt['social_context'][0]}."

        return text

    @staticmethod
    def _replace_any(text: str, source_terms: list[str], target_terms: list[str]) -> str:
        if not source_terms or not target_terms:
            return text
        out = text
        for i, term in enumerate(source_terms):
            repl = target_terms[i % len(target_terms)]
            out = re.sub(rf"\b{re.escape(term)}\b", repl, out, flags=re.IGNORECASE)
        return out
