from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, List

import pandas as pd

from .types import AdaptationItem, AdaptationResult


def load_items(path: str | Path) -> List[AdaptationItem]:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(path)

    if path.suffix.lower() == ".jsonl":
        return _load_jsonl(path)
    if path.suffix.lower() == ".csv":
        return _load_csv(path)

    raise ValueError("Input must be .jsonl or .csv")


def write_results_jsonl(results: Iterable[AdaptationResult], out_path: str | Path) -> None:
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as f:
        for r in results:
            f.write(json.dumps(r.to_dict(), ensure_ascii=False) + "\n")


def _load_jsonl(path: Path) -> List[AdaptationItem]:
    items: List[AdaptationItem] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            items.append(_row_to_item(row))
    return items


def _load_csv(path: Path) -> List[AdaptationItem]:
    df = pd.read_csv(path)
    return [_row_to_item(r) for r in df.to_dict(orient="records")]


def _row_to_item(row: dict) -> AdaptationItem:
    return AdaptationItem(
        id=str(row.get("id", "")),
        text=row["text"],
        source_culture=row["source_culture"],
        target_culture=row["target_culture"],
        genre=row.get("genre", "general"),
        metadata=row.get("metadata"),
    )
