from __future__ import annotations

import argparse
import json
from pathlib import Path

from datasets import load_dataset


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare EECC story prompts as external adaptation input")
    parser.add_argument("--output", type=str, default="data/external/eecc_story_external_120.jsonl")
    parser.add_argument("--n", type=int, default=120)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    ds = load_dataset("shaily99/eecc", "prompts", split="story")
    ds = ds.shuffle(seed=args.seed).select(range(min(args.n, len(ds))))

    targets = [
        "north_region",
        "south_region",
        "east_region",
        "west_region",
        "central_region",
        "northeast_region",
    ]

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)

    with out.open("w", encoding="utf-8") as f:
        for i, row in enumerate(ds):
            target = targets[i % len(targets)]
            item = {
                "id": f"eecc-story-{i+1:04d}",
                "text": row.get("prompt", "").strip(),
                "source_culture": "global_generic",
                "target_culture": target,
                "genre": "story",
                "metadata": {
                    "eecc_identity": row.get("identity"),
                    "eecc_topic": row.get("concept"),
                    "eecc_category": row.get("topic"),
                    "eecc_template": row.get("template"),
                },
            }
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

    print(f"Prepared {len(ds)} EECC story samples -> {out}")


if __name__ == "__main__":
    main()
