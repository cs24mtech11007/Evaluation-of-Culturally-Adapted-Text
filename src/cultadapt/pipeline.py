from __future__ import annotations

import json
from pathlib import Path
from typing import List

import pandas as pd
from tqdm import tqdm

from .adapter import CulturalAdapter
from .culture_registry import CultureRegistry
from .datasets import load_items, write_results_jsonl
from .eval_metrics import evaluate_pair
from .llm_client import LLMClient, LLMConfig
from .llm_judge import LLMJudge


def run_pipeline(
    input_path: str | Path,
    output_dir: str | Path,
    culture_config: str | Path,
    prompt_template: str | Path,
    rubric_path: str | Path,
    with_judge: bool = False,
    llm_backend: str | None = "ollama",
) -> None:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    items = load_items(input_path)
    llm_client = LLMClient(LLMConfig(backend=llm_backend)) if llm_backend else None
    adapter = CulturalAdapter(
        culture_config=culture_config,
        prompt_template=prompt_template,
        llm_client=llm_client,
    )
    registry = CultureRegistry(culture_config)
    judge = LLMJudge(rubric_path=rubric_path, llm_client=llm_client) if with_judge else None

    results = []
    metric_rows: List[dict] = []

    for item in tqdm(items, desc="Adapting"):
        result = adapter.adapt(item)
        results.append(result)

        src_profile = registry.get(item.source_culture)
        tgt_profile = registry.get(item.target_culture)

        metrics = evaluate_pair(
            source_text=item.text,
            adapted_text=result.adapted_text,
            source_profile=src_profile,
            target_profile=tgt_profile,
        )

        row = {
            "id": item.id,
            "source_culture": item.source_culture,
            "target_culture": item.target_culture,
            "genre": item.genre,
            **metrics,
        }

        if judge:
            row.update(
                judge.score(
                    source_text=item.text,
                    adapted_text=result.adapted_text,
                    source_profile=src_profile,
                    target_profile=tgt_profile,
                )
            )

        metric_rows.append(row)

    write_results_jsonl(results, output_dir / "adaptations.jsonl")

    df = pd.DataFrame(metric_rows)
    df.to_csv(output_dir / "metrics.csv", index=False)

    summary = {
        "count": int(len(df)),
        "avg_content_similarity": _safe_mean(df, "content_similarity"),
        "avg_target_culture_signal": _safe_mean(df, "target_culture_signal"),
        "avg_adaptation_depth": _safe_mean(df, "adaptation_depth"),
        "avg_lexical_shift": _safe_mean(df, "lexical_shift"),
        "avg_stereotype_risk": _safe_mean(df, "stereotype_risk"),
        "avg_composite_score": _safe_mean(df, "composite_score"),
    }

    if with_judge:
        for c in ["judge_authenticity", "judge_faithfulness", "judge_coherence", "judge_safety"]:
            summary[f"avg_{c}"] = _safe_mean(df, c)

    with (output_dir / "summary.json").open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)


def _safe_mean(df: pd.DataFrame, col: str):
    if col not in df.columns:
        return None
    values = pd.to_numeric(df[col], errors="coerce").dropna()
    if values.empty:
        return None
    return round(float(values.mean()), 4)
