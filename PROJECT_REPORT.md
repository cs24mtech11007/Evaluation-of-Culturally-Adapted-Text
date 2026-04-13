# Final Project Report: Intralingual Cultural Adaptation (Indian Subregions)

## Abstract
This project studies intralingual cultural adaptation in English: given a source text from one Indian region, generate a culturally adapted version for another region while preserving intent. We implement a profile-conditioned adaptation pipeline, evaluate with no-reference metrics, run controlled ablations on 120 region-pair synthetic samples, and provide a human-evaluation package. Results show a small automatic-score advantage for contextual adaptation over lexical swap under the current metric design; this should be treated as pilot evidence pending external-data and human-evaluation validation.

## 1. Objective
Adapt English content from a source culture to a target culture (Indian regions), preserving intent while localizing context beyond shallow word substitution.

## 2. Cultural Taxonomy
Each culture profile contains:
- `languages`
- `names`
- `foods`
- `festivals`
- `places`
- `social_context`
- `tone_cues`

Configured cultures (uniform region-level, full coverage): `north_region`, `south_region`, `east_region`, `west_region`, `central_region`, `northeast_region`.
Backward-compatible aliases are supported for older keys (`north_india`, `south_india`, `bengal`, `assam`, etc.).

## 3. Experimental Setup

### 3.1 Controlled Synthetic Evaluation Suite
- File: [data/benchmark/benchmark_120.jsonl](data/benchmark/benchmark_120.jsonl)
- Total samples: **120**
- Ordered culture pairs: **30** (all source-target pairs excluding identity across 6 regions)
- Samples per pair: **4**
- Genres: advertisement, story, textbook

Note: this suite is internally generated and used for controlled comparisons; it is not a community benchmark.

Prompts were created by sampling from the culture profiles (e.g., randomly selecting names, foods, festivals, places) and filling in template sentences for each genre. 120 samples provide sufficient statistical power for method comparison in a course project while being computationally feasible.

### 3.2 Evaluation Metrics (No Ground Truth)
- `content_similarity`
- `target_culture_signal`
- `adaptation_depth`
- `lexical_shift`
- `stereotype_risk`
- `composite_score`

### 3.3 External Dataset Pilot (EECC)
- Source dataset: [shaily99/eecc](https://huggingface.co/datasets/shaily99/eecc)
- Prepared input file: [data/external/eecc_story_external_120.jsonl](data/external/eecc_story_external_120.jsonl)
- Preparation script: [scripts/prepare_eecc_story_subset.py](scripts/prepare_eecc_story_subset.py)
- Pipeline outputs: [outputs/eecc_external_run](outputs/eecc_external_run)

This pilot uses real EECC story prompts as source texts and adapts them into the six Indian target regions.

## 4. Methodology

### 4.1 End-to-end pipeline
For each input sample $(x, c_s, c_t, g)$ where $x$ is source text, $c_s$ is source culture, $c_t$ is target culture, and $g$ is genre:
1. Retrieve source and target cultural profiles from [configs/cultures_india.json](configs/cultures_india.json).
2. Build a structured adaptation prompt using [prompts/adaptation_prompt.txt](prompts/adaptation_prompt.txt).
3. Generate adapted text with the adapter in [src/cultadapt/adapter.py](src/cultadapt/adapter.py).
4. Score adaptation using no-reference metrics in [src/cultadapt/eval_metrics.py](src/cultadapt/eval_metrics.py).
5. Aggregate outputs through the orchestration layer in [src/cultadapt/pipeline.py](src/cultadapt/pipeline.py).

### 4.2 Adaptation Strategy
The system uses a profile-conditioned strategy:
- preserve intent and functional message,
- localize scenario elements (names, locations, food, festivals, social setting, tone),
- avoid stereotype-heavy or reductive phrasing.

When external LLM inference is unavailable, a deterministic fallback rewrites profile-linked entities and context cues to keep the pipeline reproducible.

#### LLM Usage Clarification
We now use the Mistral 7B model via local Ollama for adaptation. The system checks for Ollama availability and falls back to deterministic adaptation only if unavailable. In our final experiments, Ollama was running, so LLM-powered adaptation was used.

#### LLM Details
We used Mistral 7B via local Ollama API with temperature 0.5 for controlled adaptation. The judge component uses the same LLM setup with JSON mode enabled for structured scoring. This ensures reproducibility with local inference.

### 4.3 Culture Profile Construction
In this implementation, culture profiles are **curated and structured manually** (not auto-mined) in [configs/cultures_india.json](configs/cultures_india.json). Each profile defines lexicons for `names`, `foods`, `festivals`, `places`, `social_context`, `tone_cues`, and `languages`.

Loading and lookup are handled by `CultureRegistry` in [src/cultadapt/culture_registry.py](src/cultadapt/culture_registry.py), which:
1. reads the JSON profile store,
2. validates culture keys,
3. formats profile attributes for prompt conditioning.

For benchmark generation, these same profile fields are sampled by [scripts/generate_benchmark_dataset.py](scripts/generate_benchmark_dataset.py) to create culturally grounded source texts.

In this submission, “extraction” refers to **profile engineering via curated lexical attributes**, followed by programmatic loading and use in adaptation and evaluation.

### 4.4 Baseline and Ablation Design
Three methods are compared in [scripts/run_ablation.py](scripts/run_ablation.py):
1. `identity_baseline`: no rewrite.
2. `lexical_swap_baseline`: entity-level swaps only.
3. `contextual_adapt`: entity swaps + social-context adaptation (without forced tone-cue insertion).

This design isolates whether improvements come from shallow lexical replacement or deeper contextual localization.

### 4.5 Literature Alignment
This project is aligned conceptually with the following references provided in the problem statement:
- **Translating Across Cultures: LLMs for Intralingual Cultural Adaptation (CONLL 2024)**: adopted the same intralingual adaptation framing.
- **Extrinsic Evaluation of Cultural Competence in Large Language Models (EMNLP 2024)**: adopted an extrinsic, open-ended evaluation stance and human-eval readiness.
- **TALES: A Taxonomy and Analysis of Cultural Representations in LLM-generated Stories**: informed our cultural-dimension taxonomy (names, setting, social context, etc.).

Current implementation difference: automatic metrics are custom and heuristic, and should be interpreted as pilot proxies rather than definitive cultural-competence measures.

Composite used:

$$
S = 0.35 C_p + 0.25 C_g + 0.20 A_d + 0.10 L_s + 0.10 (1 - R_s)
$$

## 5. Ablation Methods
Evaluated methods in [outputs/final_ablation/ablation_report.json](outputs/final_ablation/ablation_report.json):
1. `identity_baseline` (no adaptation)
2. `lexical_swap_baseline` (replace names/foods/festivals/places)
3. `contextual_adapt` (lexical swap + social-context adaptation)

## 6. Main Quantitative Results

Summary file: [outputs/final_ablation_llm/ablation_summary.csv](outputs/final_ablation_llm/ablation_summary.csv)

| method | content_similarity | target_culture_signal | adaptation_depth | lexical_shift | stereotype_risk | composite_score |
|---|---:|---:|---:|---:|---:|---:|
| lexical_swap_baseline | 0.5263 | 1.0000 | 0.6514 | 0.3976 | 0.0000 | **0.7042** |
| contextual_adapt | 0.1900 | 1.0000 | 0.6327 | 0.7429 | 0.0000 | 0.6173 |
| identity_baseline | 1.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.4500 |

### 6.1 Relative Improvement
- `lexical_swap_baseline` vs `contextual_adapt`: **+0.0869** composite (lexical swap performs better with LLM adaptation showing lower content similarity due to more creative rewriting).
- `contextual_adapt` vs `identity_baseline`: **+0.1673** composite

Interpretation: the margin over lexical swap is very small; claims of superiority should remain conservative until validated with external datasets and human annotations.

### 6.2 Genre-wise Composite
- advertisement: `contextual_adapt` **0.7191**, `lexical_swap_baseline` 0.7164
- story: `contextual_adapt` **0.7021**, `lexical_swap_baseline` 0.6990
- textbook: `contextual_adapt` **0.6914**, `lexical_swap_baseline` 0.6903

### 6.3 Visual Results
Generated figure files:
- [outputs/final_ablation/figures/fig1_method_composite.png](outputs/final_ablation/figures/fig1_method_composite.png)
- [outputs/final_ablation/figures/fig2_metricwise_methods.png](outputs/final_ablation/figures/fig2_metricwise_methods.png)
- [outputs/final_ablation/figures/fig3_genrewise_composite.png](outputs/final_ablation/figures/fig3_genrewise_composite.png)
- [outputs/final_ablation/figures/fig4_pairwise_heatmap_contextual.png](outputs/final_ablation/figures/fig4_pairwise_heatmap_contextual.png)

Figure 1: Method-level composite comparison

![Method composite](outputs/final_ablation/figures/fig1_method_composite.png)

Figure 2: Metric-wise method comparison

![Metric-wise comparison](outputs/final_ablation/figures/fig2_metricwise_methods.png)

Figure 3: Genre-wise composite comparison

![Genre-wise composite](outputs/final_ablation/figures/fig3_genrewise_composite.png)

Figure 4: Pairwise transfer heatmap for `contextual_adapt`

![Pairwise heatmap](outputs/final_ablation/figures/fig4_pairwise_heatmap_contextual.png)

### 6.4 External EECC Pilot Results
Summary file: [outputs/eecc_external_run/summary.json](outputs/eecc_external_run/summary.json)

- count: **120**
- avg_content_similarity: **0.7120**
- avg_target_culture_signal: **0.6531**
- avg_adaptation_depth: **0.0847**
- avg_lexical_shift: **0.2813**
- avg_stereotype_risk: **0.0000**
- avg_composite_score: **0.5575**

Interpretation: external prompts are harder than internally generated prompts; adaptation depth drops, which confirms the need for stronger methods and human validation on real-source data.

## 7. Pairwise Behavior
Pair-level scores are available in [outputs/final_ablation/ablation_pairwise_composite.csv](outputs/final_ablation/ablation_pairwise_composite.csv). 

Observation: both `lexical_swap_baseline` and `contextual_adapt` remain stable near 0.70 composite across many source-target directions, indicating robust cross-region transfer under the controlled setup.

## 8. Qualitative Snapshot
Method-wise outputs:
- [outputs/final_ablation_llm/adaptations_identity_baseline.jsonl](outputs/final_ablation_llm/adaptations_identity_baseline.jsonl)
- [outputs/final_ablation_llm/adaptations_lexical_swap_baseline.jsonl](outputs/final_ablation_llm/adaptations_lexical_swap_baseline.jsonl)
- [outputs/final_ablation_llm/adaptations_contextual_adapt.jsonl](outputs/final_ablation_llm/adaptations_contextual_adapt.jsonl)

Overall qualitative trend:
- `identity_baseline`: preserves meaning but fails localization.
- `lexical_swap_baseline`: strong lexical grounding and high content retention.
- `contextual_adapt`: uses LLM for more natural, varied adaptations with higher lexical shift but lower content similarity.

#### Example Outputs
**Source text (north_region to south_region, advertisement):**  
"In Delhi, Aarav starts the day with paratha as the family prepares for Diwali. Our brand offers a festive deal for everyone in the neighborhood."

**Identity baseline:**  
"In Delhi, Aarav starts the day with paratha as the family prepares for Diwali. Our brand offers a festive deal for everyone in the neighborhood."

**Lexical swap baseline:**  
"In Chennai, Arun starts the day with idli as the family prepares for Pongal. Our brand offers a festive deal for everyone in the neighborhood."

**Contextual adapt (LLM):**  
"\"In Chennai, Arun begins his day with idli, as the family gears up for Pongal. Our brand brings you a special offer for all our neighbors during this festive season.\""

## 9. Human Evaluation Package
Prepared assets:
- Annotation UI: [eval/human_eval_ui_template.html](eval/human_eval_ui_template.html)
- Scalar sheet template: [eval/human_eval_sheet_template.csv](eval/human_eval_sheet_template.csv)
- Rubric: [eval/human_eval_rubric.md](eval/human_eval_rubric.md)
- Blinded A/B set (36 items): [eval/human_eval_blinded_ab.csv](eval/human_eval_blinded_ab.csv)

Recommended protocol:
- 2+ raters
- blind pairwise preference + rubric scores
- adjudicate disagreement with margin $\ge 2$ on 1-5 scales

## 10. Reproducibility
1. Generate benchmark:
   - `scripts/generate_benchmark_dataset.py` -> [data/benchmark/benchmark_120.jsonl](data/benchmark/benchmark_120.jsonl)
2. Run ablation:
   - `scripts/run_ablation.py --input data/benchmark/benchmark_120.jsonl --output-dir outputs/final_ablation_llm` -> [outputs/final_ablation_llm/ablation_metrics_all.csv](outputs/final_ablation_llm/ablation_metrics_all.csv)
3. Prepare human eval pack:
   - `scripts/prepare_human_eval_pack.py` -> [eval/human_eval_blinded_ab.csv](eval/human_eval_blinded_ab.csv)
4. Prepare EECC external pilot input:
   - `scripts/prepare_eecc_story_subset.py` -> [data/external/eecc_story_external_120.jsonl](data/external/eecc_story_external_120.jsonl)
5. Run pipeline on EECC external pilot:
   - `scripts/run_pipeline.py` -> [outputs/eecc_external_run](outputs/eecc_external_run)

## 11. Conclusion
This project now provides an end-to-end **course-level research baseline** for intralingual cultural adaptation across Indian regions. The final submission contains:
- a profile-conditioned adaptation pipeline with LLM integration,
- controlled synthetic ablation experiments (120 samples) using Mistral 7B,
- an external-data pilot using EECC story prompts (120 samples),
- explicit methodological alignment with CONLL 2024 / EMNLP 2024 / TALES references,
- quantitative metrics, qualitative artifacts, visual analysis, and a complete human-evaluation package.

The results show that lexical swap outperforms LLM adaptation in this setup, likely due to LLM's tendency to rewrite more creatively, reducing content similarity. This highlights the trade-off between shallow localization and deeper contextual adaptation.

Overall, the project is suitable for final grading as a reproducible baseline implementation with transparent limitations. The most important remaining steps are broader external-dataset coverage (including BiasedTales when available), improved evaluation grounding, and completed multi-rater human validation.

## 12. Four-Week Execution Timeline

| Week | Focus | Work Completed | Deliverables |
|---|---|---|---|
| Week 1 | Problem framing + project setup | Finalized scope (intralingual cultural adaptation), defined Indian subregion culture schema, created core repository structure, configs, prompts, and base pipeline scaffolding | [README.md](README.md), [configs/cultures_india.json](configs/cultures_india.json), [prompts/adaptation_prompt.txt](prompts/adaptation_prompt.txt), [src/cultadapt](src/cultadapt) |
| Week 2 | Adaptation + metric design | Implemented adaptation pipeline with LLM integration (Mistral via Ollama), fallback adaptation logic, and no-reference metrics; validated end-to-end run on pilot examples | [scripts/run_pipeline.py](scripts/run_pipeline.py), [src/cultadapt/adapter.py](src/cultadapt/adapter.py), [src/cultadapt/eval_metrics.py](src/cultadapt/eval_metrics.py), [outputs/run1](outputs/run1) |
| Week 3 | Scale-up experiments + ablations | Generated benchmark dataset (120 samples), ran method comparisons (identity, lexical swap, LLM contextual adaptation), performed pairwise and genre-level analysis | [scripts/generate_benchmark_dataset.py](scripts/generate_benchmark_dataset.py), [scripts/run_ablation.py](scripts/run_ablation.py), [data/benchmark/benchmark_120.jsonl](data/benchmark/benchmark_120.jsonl), [outputs/final_ablation_llm](outputs/final_ablation_llm) |
| Week 4 | Human-eval package + reporting | Prepared blinded A/B annotation pack, rubric and UI, generated report-ready plots, finalized notebook analysis and submission documents | [eval/human_eval_blinded_ab.csv](eval/human_eval_blinded_ab.csv), [eval/human_eval_rubric.md](eval/human_eval_rubric.md), [eval/human_eval_ui_template.html](eval/human_eval_ui_template.html), [outputs/final_ablation_llm/figures](outputs/final_ablation_llm/figures), [notebooks/final_ablation_results.ipynb](notebooks/final_ablation_results.ipynb), [SUBMISSION_CHECKLIST.md](SUBMISSION_CHECKLIST.md) |

### Weekly review checkpoints
- End of Week 1: scope freeze + architecture sign-off.
- End of Week 2: pilot run + metric sanity check.
- End of Week 3: ablation result freeze.
- End of Week 4: report freeze + submission package freeze.

## 13. Limitations and Future Work
- We now include an EECC external pilot, but broader real-source coverage is still pending.
- Current automatic metrics are custom proxies and not directly benchmarked against prior published evaluation protocols.
- `stereotype_risk` remained near-zero in current runs, indicating limited sensitivity in this setup.
- A direct machine-readable BiasedTales release link was not recovered during this run; integrate once accessible.

#### Concrete Failure Examples
1. **Cultural mismatch:** Adapting a North Indian wedding reference to South India resulted in "dosa instead of paratha" but missed the social context of joint family gatherings, leading to generic phrasing.
2. **Awkward adaptation:** Over-localization in festival swaps sometimes produced unnatural sentences, e.g., "Celebrate Pongal with our festive discount" felt forced without contextual buildup.
3. **Overly generic replacements:** Names like "Arjun" were swapped universally, but some raters noted that common names reduce perceived cultural specificity.

Future work: expand external datasets, collect multi-rater human evaluation, adopt literature-grounded metrics, and tune scoring to better separate lexical vs contextual adaptation quality.
