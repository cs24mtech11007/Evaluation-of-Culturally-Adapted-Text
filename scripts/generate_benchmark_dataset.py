from __future__ import annotations

import argparse
import json
import random
from itertools import product
from pathlib import Path


def build_templates():
    return {
        "advertisement": [
            "In {place}, {name} starts the day with {food} as the family prepares for {festival}. Our brand offers a festive deal for everyone in the neighborhood.",
            "{name} from {place} chooses {food} during {festival} celebrations, and recommends our product for every family gathering.",
        ],
        "story": [
            "On a busy morning in {place}, {name} and family share {food} before joining the {festival} celebrations in the local community.",
            "{name} grew up in {place}, where {food} and {festival} memories shaped the family's daily routines and conversations.",
        ],
        "textbook": [
            "A classroom example from {place}: {name} buys ingredients for {food} before {festival}. Discuss how local context influences consumer behavior.",
            "Case study: In {place}, {name} plans a community event around {festival} and serves {food}. Identify culturally grounded decision factors.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate synthetic benchmark set for cultural adaptation")
    parser.add_argument(
        "--culture-config",
        default="configs/cultures_india.json",
        type=str,
        help="Path to culture profile JSON",
    )
    parser.add_argument(
        "--output",
        default="data/benchmark/benchmark_120.jsonl",
        type=str,
        help="Output JSONL path",
    )
    parser.add_argument("--samples-per-pair", default=4, type=int)
    parser.add_argument("--seed", default=42, type=int)
    args = parser.parse_args()

    random.seed(args.seed)

    with Path(args.culture_config).open("r", encoding="utf-8") as f:
        raw = json.load(f)

    cultures = {k: v for k, v in raw.items() if not str(k).startswith("_")}

    keys = list(cultures.keys())
    templates = build_templates()
    genres = list(templates.keys())

    rows = []
    uid = 1
    for source_c, target_c in product(keys, keys):
        if source_c == target_c:
            continue
        for k in range(args.samples_per_pair):
            genre = genres[k % len(genres)]
            t = templates[genre][k % len(templates[genre])]
            src = cultures[source_c]
            text = t.format(
                place=src["places"][k % len(src["places"])],
                name=src["names"][k % len(src["names"])],
                food=src["foods"][k % len(src["foods"])],
                festival=src["festivals"][k % len(src["festivals"])],
            )
            rows.append(
                {
                    "id": f"bm-{uid:04d}",
                    "text": text,
                    "source_culture": source_c,
                    "target_culture": target_c,
                    "genre": genre,
                }
            )
            uid += 1

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    print(f"Wrote {len(rows)} samples to {out}")


if __name__ == "__main__":
    main()
