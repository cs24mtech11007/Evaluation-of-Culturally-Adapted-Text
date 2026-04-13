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
            raise RuntimeError("LLM adaptation required but LLM backend is not available. Please ensure Ollama or another LLM backend is running.")

        return AdaptationResult(
            id=item.id,
            source_text=item.text,
            adapted_text=adapted,
            source_culture=item.source_culture,
            target_culture=item.target_culture,
            genre=item.genre,
            metadata=item.metadata,
        )
