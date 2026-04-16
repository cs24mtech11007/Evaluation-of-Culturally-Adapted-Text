from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare human evaluation sheet for LLM adaptation")
    parser.add_argument("--ablation-csv", type=str, default="outputs/final_ablation/ablation_metrics_all.csv")
    parser.add_argument("--output", type=str, default="eval/human_eval_blinded_ab.csv")
    parser.add_argument("--sample-size", type=int, default=36)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    df = pd.read_csv(args.ablation_csv)

    llm = df[df["method"] == "llm_adaptation"].copy()
    if llm.empty:
        raise ValueError("No rows found for method 'llm_adaptation' in ablation CSV")

    keep_cols = ["id", "source_culture", "target_culture", "genre", "source_text", "adapted_text"]
    merged = llm[keep_cols].copy()

    if args.sample_size < len(merged):
        merged = merged.sample(args.sample_size, random_state=args.seed)

    rows = []
    for _, r in merged.iterrows():
        cand_a = r["adapted_text"]
        cand_b = ""
        label_map = "A=llm_adaptation;B=none"

        rows.append(
            {
                "item_id": r["id"],
                "source_culture": r["source_culture"],
                "target_culture": r["target_culture"],
                "genre": r["genre"],
                "source_text": r["source_text"],
                "candidate_a": cand_a,
                "candidate_b": cand_b,
                "preferred_candidate_A_or_B": "",
                "faithfulness_winner_A_or_B": "",
                "authenticity_winner_A_or_B": "",
                "safety_issue_yes_no": "",
                "comments": "",
                "hidden_label_map_do_not_show_to_annotators": label_map,
            }
        )

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(out, index=False)
    print(f"Wrote {len(rows)} rows to {out}")


if __name__ == "__main__":
    main()
