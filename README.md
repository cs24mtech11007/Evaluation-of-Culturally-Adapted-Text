# Intralingual Cultural Adaptation Project (Indian Subregions)

This project builds a complete pipeline for adapting content from a source culture to a target culture within the same language (English), with a special focus on Indian subregions.

## Problem
Given text grounded in one culture, generate an adapted version for another culture such that:
- core intent and message are preserved,
- superficial word replacement is avoided,
- context (setting, references, social norms, examples, tone) is meaningfully adapted.

Examples: ad scripts, stories, textbook examples.

## Why this setup
You highlighted two constraints:
1. Adaptation quality is open-ended (no fixed gold labels).
2. Existing datasets may not have direct ground-truth targets.

So this project uses:
- LLM-powered adaptation pipeline with structured cultural profiles,
- multi-metric evaluation without reference targets,
- optional LLM-judge rubric for qualitative depth.

The system exclusively uses LLM adaptation (no fallback methods) to ensure deep, contextual cultural localization.

## Included Datasets Support
- Generic external loaders (CSV/JSONL with text + optional culture metadata)
- Story-style external inputs

Current repository results are produced on a controlled synthetic suite for method debugging and ablation. 
For external-data evaluation, first normalize your dataset files into canonical format.

You can plug any dataset into the canonical format:

```json
{
  "id": "sample-1",
  "text": "Your source text",
   "source_culture": "north_region",
   "target_culture": "south_region",
  "genre": "ad"
}
```

## Project Structure

- [pyproject.toml](pyproject.toml)
- [requirements.txt](requirements.txt)
- [.env.example](.env.example)
- [configs/cultures_india.json](configs/cultures_india.json)
- [configs/eval_rubric.yaml](configs/eval_rubric.yaml)
- [prompts/adaptation_prompt.txt](prompts/adaptation_prompt.txt)
- [src/cultadapt/types.py](src/cultadapt/types.py)
- [src/cultadapt/culture_registry.py](src/cultadapt/culture_registry.py)
- [src/cultadapt/datasets.py](src/cultadapt/datasets.py)
- [src/cultadapt/prompts.py](src/cultadapt/prompts.py)
- [src/cultadapt/llm_client.py](src/cultadapt/llm_client.py)
- [src/cultadapt/adapter.py](src/cultadapt/adapter.py)
- [src/cultadapt/eval_metrics.py](src/cultadapt/eval_metrics.py)
- [src/cultadapt/llm_judge.py](src/cultadapt/llm_judge.py)
- [src/cultadapt/pipeline.py](src/cultadapt/pipeline.py)
- [scripts/run_pipeline.py](scripts/run_pipeline.py)
- [scripts/demo.py](scripts/demo.py)
- [tests/test_metrics.py](tests/test_metrics.py)
- [PROJECT_REPORT.md](PROJECT_REPORT.md)

## Setup

1. Create and activate a Python env.
2. Install deps:

```bash
pip install -r requirements.txt
```

For local HuggingFace backend support, also install:

```bash
pip install transformers torch
```

3. Copy env:

```bash
cp .env.example .env
```

4. Configure LLM backend and keys if you want LLM generation/judging:
- `LLM_BACKEND` (default: `ollama`, alternatives: `huggingface`)
- `OLLAMA_MODEL`, `OLLAMA_BASE_URL`, `OLLAMA_TEMPERATURE` for Ollama
- `HF_MODEL`, `HF_DEVICE` for HuggingFace local inference
- optional `OPENAI_API_KEY`, `OPENAI_MODEL` if using OpenAI backend

## Running

### Quick demo (single sample)

```bash
python scripts/demo.py
```

### Full pipeline

```bash
python scripts/run_pipeline.py \
  --input data/samples/input.jsonl \
  --output-dir outputs/run1 \
  --judge
```

Outputs:
- `adaptations.jsonl`
- `metrics.csv`
- `summary.json`

### External dataset normalization

Use [scripts/prepare_external_dataset.py](scripts/prepare_external_dataset.py) to convert raw CSV/JSONL into canonical JSONL.

Example:

```bash
python scripts/prepare_external_dataset.py \
   --input data/external/raw_external.csv \
   --output data/external/external_canonical.jsonl \
   --text-col text \
   --id-col id \
   --source-col source_culture \
   --target-col target_culture \
   --genre-col genre
```

Then run:

```bash
python scripts/run_pipeline.py \
   --input data/external/external_canonical.jsonl \
   --output-dir outputs/external_run
```

For local HuggingFace inference, set `LLM_BACKEND=huggingface` in `.env` or add `--llm-backend huggingface`.

## Evaluation Metrics (No Ground Truth)

This project computes the following:

1. Content Preservation (`content_similarity`)  
   TF-IDF cosine similarity between source and adapted text.

2. Cultural Grounding (`target_culture_signal`)  
   Density of target culture markers (food, festivals, names, places, linguistic cues), penalized if source culture markers remain dominant.

3. Adaptation Depth (`adaptation_depth`)  
   Fraction of cultural dimensions that changed (names, food, festivals, setting cues, social context).

4. Lexical Novelty (`lexical_shift`)  
   Measures non-trivial rewriting beyond direct copying.

5. Stereotype Risk (`stereotype_risk`)  
   Rule-based soft risk detector for reductive formulations (can be expanded).

6. Optional LLM Judge (`judge_*`)  
   Rubric-based scoring on authenticity, coherence, faithfulness, and safety.

Composite score:

$$
S = 0.35 C_p + 0.25 C_g + 0.20 A_d + 0.10 L_s + 0.10 (1 - R_s)
$$

where $C_p$ is content preservation, $C_g$ target grounding, $A_d$ adaptation depth, $L_s$ lexical shift, $R_s$ stereotype risk.

## Cultural Definitions (Indian Regions)

Default profiles include:
- `north_region`
- `south_region`
- `east_region`
- `west_region`
- `central_region`
- `northeast_region`

Each profile includes lexicons for names, foods, festivals, places, and language cues. Edit [configs/cultures_india.json](configs/cultures_india.json) to extend.

## Alignment with your references
- Intralingual adaptation framing (CONLL 2024 style)
- Extrinsic and open-ended evaluation (EMNLP 2024 style)
- Narrative cultural representation dimensions (TALES-like taxonomy)

## Suggested next experiments
- Human eval with pairwise preference + rubric agreement
- Add embedding-based semantic preservation (Sentence Transformers)
- Expand safety layer using dedicated stereotype/bias classifiers
- Add retrieval-grounded cultural facts for factuality
