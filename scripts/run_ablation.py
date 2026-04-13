from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import pandas as pd
from tqdm import tqdm

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from cultadapt.adapter import CulturalAdapter
from cultadapt.culture_registry import CultureRegistry
from cultadapt.datasets import load_items
from cultadapt.eval_metrics import evaluate_pair
from cultadapt.llm_client import LLMClient, LLMConfig
from cultadapt.llm_judge import LLMJudge
from cultadapt.types import AdaptationItem


def _replace_any(text: str, source_terms: list[str], target_terms: list[str]) -> str:
    if not source_terms or not target_terms:
        return text
    out = text
    for i, term in enumerate(source_terms):
        repl = target_terms[i % len(target_terms)]
        out = re.sub(rf"\b{re.escape(term)}\b", repl, out, flags=re.IGNORECASE)
    return out


def identity_baseline(text: str, *_args) -> str:
    return text


def lexical_swap_baseline(text: str, src: dict, tgt: dict) -> str:
    out = text
    out = _replace_any(out, src.get("places", []), tgt.get("places", []))
    out = _replace_any(out, src.get("foods", []), tgt.get("foods", []))
    out = _replace_any(out, src.get("festivals", []), tgt.get("festivals", []))
    out = _replace_any(out, src.get("names", []), tgt.get("names", []))
    return out


def contextual_adapt(text: str, src: dict, tgt: dict) -> str:
    out = lexical_swap_baseline(text, src, tgt)
    out = _replace_any(out, src.get("social_context", []), tgt.get("social_context", []))

    addendum = []
    if tgt.get("social_context"):
        addendum.append(f"The scene reflects {tgt['social_context'][0]}.")
    if addendum:
        out = out.rstrip() + " " + " ".join(addendum)
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description="Run ablations for cultural adaptation")
    parser.add_argument("--input", type=str, required=True)
    parser.add_argument("--culture-config", type=str, default="configs/cultures_india.json")
    parser.add_argument("--output-dir", type=str, default="outputs/final_ablation")
    parser.add_argument("--rubric-path", type=str, default="configs/eval_rubric.yaml")
    parser.add_argument("--judge", action="store_true", help="Enable LLM judge scoring via Ollama or other supported backend")
    parser.add_argument(
        "--llm-backend",
        type=str,
        default=None,
        help="Optional LLM backend override for judge scoring: ollama or huggingface",
    )
    args = parser.parse_args()

    registry = CultureRegistry(args.culture_config)
    items = load_items(args.input)
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    llm_client = LLMClient(LLMConfig(backend=args.llm_backend)) if args.llm_backend else None
    judge = LLMJudge(rubric_path=args.rubric_path, llm_client=llm_client) if args.judge else None
    if args.judge and judge and not judge.enabled:
        print("WARNING: --judge requested but the selected LLM backend is not available. Judge scores will be None.")

    adapter = CulturalAdapter(culture_config=args.culture_config, prompt_template=Path("prompts") / "adaptation_prompt.txt", llm_client=llm_client)

    def llm_adapt(item: AdaptationItem) -> str:
        result = adapter.adapt(item)
        return result.adapted_text

    methods = {
        "identity_baseline": identity_baseline,
        "lexical_swap_baseline": lexical_swap_baseline,
        "contextual_adapt": llm_adapt,  # Now uses LLM
    }

    all_rows = []
    for method_name, fn in methods.items():
        method_adapt_path = out_dir / f"adaptations_{method_name}.jsonl"
        with method_adapt_path.open("w", encoding="utf-8") as f:
            for item in tqdm(items, desc=f"{method_name}"):
                src = registry.get(item.source_culture)
                tgt = registry.get(item.target_culture)
                if method_name == "contextual_adapt":
                    adapted = fn(item)
                else:
                    adapted = fn(item.text, src, tgt)
                metrics = evaluate_pair(item.text, adapted, src, tgt)
                row = {
                    "id": item.id,
                    "method": method_name,
                    "source_culture": item.source_culture,
                    "target_culture": item.target_culture,
                    "genre": item.genre,
                    "source_text": item.text,
                    "adapted_text": adapted,
                    **metrics,
                }

                if judge:
                    row.update(
                        judge.score(
                            source_text=item.text,
                            adapted_text=adapted,
                            source_profile=src,
                            target_profile=tgt,
                        )
                    )

                all_rows.append(row)
                f.write(json.dumps({k: row[k] for k in ["id", "source_text", "adapted_text", "source_culture", "target_culture", "genre"]}, ensure_ascii=False) + "\n")

    df = pd.DataFrame(all_rows)
    df.to_csv(out_dir / "ablation_metrics_all.csv", index=False)

    metric_cols = [
        "content_similarity",
        "target_culture_signal",
        "adaptation_depth",
        "lexical_shift",
        "stereotype_risk",
        "composite_score",
    ]

    if args.judge:
        metric_cols.extend(["judge_authenticity", "judge_faithfulness", "judge_coherence", "judge_safety"])

    summary = df.groupby("method")[metric_cols].mean().reset_index().sort_values("composite_score", ascending=False)
    summary.to_csv(out_dir / "ablation_summary.csv", index=False)

    pair_table = (
        df.groupby(["method", "source_culture", "target_culture"])["composite_score"]
        .mean()
        .reset_index()
        .sort_values(["method", "composite_score"], ascending=[True, False])
    )
    pair_table.to_csv(out_dir / "ablation_pairwise_composite.csv", index=False)

    report = {
        "n_items": int(df["id"].nunique()),
        "n_rows": int(len(df)),
        "methods": list(methods.keys()),
        "best_method": summary.iloc[0]["method"],
    }
    with (out_dir / "ablation_report.json").open("w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(summary.round(4).to_string(index=False))
    print(f"Saved ablation artifacts to {out_dir}")


if __name__ == "__main__":
    main()
