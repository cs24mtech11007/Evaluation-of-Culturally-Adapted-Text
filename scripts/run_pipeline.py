from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from cultadapt.pipeline import run_pipeline


def main() -> None:
    parser = argparse.ArgumentParser(description="Run cultural adaptation pipeline")
    parser.add_argument("--input", type=str, required=True, help="Path to input .jsonl/.csv")
    parser.add_argument("--output-dir", type=str, required=True, help="Path to output directory")
    parser.add_argument(
        "--culture-config",
        type=str,
        default=str(Path("configs") / "cultures_india.json"),
    )
    parser.add_argument(
        "--prompt-template",
        type=str,
        default=str(Path("prompts") / "adaptation_prompt.txt"),
    )
    parser.add_argument(
        "--rubric-path",
        type=str,
        default=str(Path("configs") / "eval_rubric.yaml"),
    )
    parser.add_argument("--judge", action="store_true", help="Enable LLM judge scoring")
    parser.add_argument(
        "--llm-backend",
        type=str,
        default=None,
        help="Optional LLM backend override: ollama or huggingface",
    )
    args = parser.parse_args()

    run_pipeline(
        input_path=args.input,
        output_dir=args.output_dir,
        culture_config=args.culture_config,
        prompt_template=args.prompt_template,
        rubric_path=args.rubric_path,
        with_judge=args.judge,
        llm_backend=args.llm_backend,
    )


if __name__ == "__main__":
    main()
