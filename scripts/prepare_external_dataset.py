from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


def _read_any(path: Path) -> pd.DataFrame:
    if path.suffix.lower() == ".csv":
        return pd.read_csv(path)
    if path.suffix.lower() == ".jsonl":
        rows = []
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line:
                rows.append(json.loads(line))
        return pd.DataFrame(rows)
    raise ValueError("Input must be .csv or .jsonl")


def main() -> None:
    parser = argparse.ArgumentParser(description="Normalize external dataset to canonical cultural adaptation format")
    parser.add_argument("--input", required=True, help="Path to EECC/BiasedTales-style CSV/JSONL")
    parser.add_argument("--output", required=True, help="Path to canonical output JSONL")

    # Column mapping
    parser.add_argument("--id-col", default="id")
    parser.add_argument("--text-col", default="text")
    parser.add_argument("--source-col", default="source_culture")
    parser.add_argument("--target-col", default="target_culture")
    parser.add_argument("--genre-col", default="genre")

    # Defaults when source/target/genre are not in dataset
    parser.add_argument("--default-source", default="north_region")
    parser.add_argument("--default-target", default="south_region")
    parser.add_argument("--default-genre", default="general")
    args = parser.parse_args()

    inp = Path(args.input)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)

    df = _read_any(inp)
    if args.text_col not in df.columns:
        raise ValueError(f"Missing text column: {args.text_col}")

    rows = []
    for i, r in df.reset_index(drop=True).iterrows():
        item_id = str(r[args.id_col]) if args.id_col in df.columns and pd.notna(r[args.id_col]) else f"ext-{i+1:05d}"
        source = r[args.source_col] if args.source_col in df.columns and pd.notna(r[args.source_col]) else args.default_source
        target = r[args.target_col] if args.target_col in df.columns and pd.notna(r[args.target_col]) else args.default_target
        genre = r[args.genre_col] if args.genre_col in df.columns and pd.notna(r[args.genre_col]) else args.default_genre

        rows.append(
            {
                "id": item_id,
                "text": str(r[args.text_col]),
                "source_culture": str(source),
                "target_culture": str(target),
                "genre": str(genre),
            }
        )

    with out.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    print(f"Normalized {len(rows)} rows -> {out}")


if __name__ == "__main__":
    main()
