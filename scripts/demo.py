from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from cultadapt.pipeline import run_pipeline


def main() -> None:
    base = Path("data") / "samples"
    base.mkdir(parents=True, exist_ok=True)
    input_path = base / "input.jsonl"

    sample = {
        "id": "ad-1",
        "text": "This winter in Delhi, Rohan starts his day with hot parathas and lassi before heading to the market. Celebrate Diwali with our festive discount.",
        "source_culture": "north_region",
        "target_culture": "south_region",
        "genre": "advertisement",
    }

    with input_path.open("w", encoding="utf-8") as f:
        f.write(json.dumps(sample, ensure_ascii=False) + "\n")

    run_pipeline(
        input_path=input_path,
        output_dir=Path("outputs") / "demo",
        culture_config=Path("configs") / "cultures_india.json",
        prompt_template=Path("prompts") / "adaptation_prompt.txt",
        rubric_path=Path("configs") / "eval_rubric.yaml",
        with_judge=False,
    )

    print("Demo completed. Check outputs/demo/")


if __name__ == "__main__":
    main()
