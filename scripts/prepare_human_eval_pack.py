from __future__ import annotations

import argparse
import random
from pathlib import Path

import pandas as pd


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare blinded A/B sheet for human evaluation")
    parser.add_argument("--ablation-csv", type=str, default="outputs/final_ablation/ablation_metrics_all.csv")
    parser.add_argument("--output", type=str, default="eval/human_eval_blinded_ab.csv")
    parser.add_argument("--sample-size", type=int, default=36)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    random.seed(args.seed)
    df = pd.read_csv(args.ablation_csv)

    a = df[df["method"] == "lexical_swap_baseline"].copy()
    b = df[df["method"] == "contextual_adapt"].copy()

    keep_cols = ["id", "source_culture", "target_culture", "genre", "source_text", "adapted_text"]
    merged = a[keep_cols].merge(
        b[["id", "adapted_text"]].rename(columns={"adapted_text": "adapted_text_b"}),
        on="id",
        how="inner",
    ).rename(columns={"adapted_text": "adapted_text_a"})

    if args.sample_size < len(merged):
        merged = merged.sample(args.sample_size, random_state=args.seed)

    rows = []
    for _, r in merged.iterrows():
        if random.random() < 0.5:
            cand_a, cand_b = r["adapted_text_a"], r["adapted_text_b"]
            label_map = "A=lexical_swap_baseline;B=contextual_adapt"
        else:
            cand_a, cand_b = r["adapted_text_b"], r["adapted_text_a"]
            label_map = "A=contextual_adapt;B=lexical_swap_baseline"

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
