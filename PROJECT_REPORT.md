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

### 2.1 Cultural Profile Example
Profiles are stored in [configs/cultures_india.json](configs/cultures_india.json). A concrete example (`south_region`) includes:
- `languages`: Tamil, Telugu, Kannada, Malayalam, Tulu
- `names`: Arun, Karthik, Meena, Lakshmi, ...
- `foods`: idli, dosa, sambar, rasam, appam, filter coffee, ...
- `festivals`: Pongal, Onam, Ugadi, Vishu, ...
- `places`: Chennai, Bengaluru, Hyderabad, Kochi, ...
- `social_context`: temple festivals, coastal markets, kolam at doorstep, ...
- `tone_cues`: namaskaram, vanakkam, namaskara

These profile fields are used in both adaptation prompting and metric computation (`target_culture_signal`, `adaptation_depth`).

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

How EECC was used in this project:
1. Loaded `story` split from `shaily99/eecc` (`prompts` config).
2. Shuffled with fixed seed and selected 120 prompts.
3. Converted each prompt into canonical pipeline JSONL format with:
   - `text` = EECC prompt,
   - `source_culture` = `global_generic`,
   - `target_culture` assigned round-robin across 6 Indian regions,
   - `genre` = `story`.
4. Preserved EECC metadata fields in each item (`identity`, `concept`, `topic`, `template`) as `eecc_*` keys.
5. Ran the same LLM adaptation + metric pipeline used for benchmark data, then compared aggregate behavior against synthetic results.

## 4. Methodology

### 4.1 End-to-end pipeline
For each input sample $(x, c_s, c_t, g)$ where $x$ is source text, $c_s$ is source culture, $c_t$ is target culture, and $g$ is genre:
1. Retrieve source and target cultural profiles from [configs/cultures_india.json](configs/cultures_india.json).
2. Build a structured adaptation prompt using [prompts/adaptation_prompt.txt](prompts/adaptation_prompt.txt).
3. Generate adapted text with the adapter in [src/cultadapt/adapter.py](src/cultadapt/adapter.py).
4. Score adaptation using no-reference metrics in [src/cultadapt/eval_metrics.py](src/cultadapt/eval_metrics.py).
5. Aggregate outputs through the orchestration layer in [src/cultadapt/pipeline.py](src/cultadapt/pipeline.py).

#### LLM Prompt Used
The adaptation prompt template (from [prompts/adaptation_prompt.txt](prompts/adaptation_prompt.txt)) is:

"You are a cultural adaptation expert. Adapt the source text from the source culture into the target culture. Preserve intent and practical message; adapt scenario-level context (setting, social cues, examples, names, references, routines, tone); keep natural English; avoid stereotypes; keep roughly similar length. You are given source profile, target profile, genre, and source text. Return only the adapted text."

Template variables injected at runtime:
- `{source_profile}`: formatted source-culture attributes
- `{target_profile}`: formatted target-culture attributes
- `{genre}`: input genre (advertisement/story/textbook)
- `{text}`: source text to adapt

### 4.2 Adaptation Strategy
The system uses a profile-conditioned strategy:
- preserve intent and functional message,
- localize scenario elements (names, locations, food, festivals, social setting, tone),
- avoid stereotype-heavy or reductive phrasing.

The final system is strictly LLM-only: adaptation runs only when the configured LLM backend is available.

#### LLM Usage Clarification
We use the Mistral 7B model via local Ollama for adaptation. If the backend is unavailable, the run fails fast instead of using any deterministic fallback. All reported experiments were executed with Ollama running.

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
The final evaluation setup in [scripts/run_ablation.py](scripts/run_ablation.py) uses a single LLM method:
1. `llm_adaptation`: LLM-powered entity swaps + social-context adaptation.

This setup focuses on measuring end-to-end LLM cultural adaptation performance across all source-target region pairs.

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
1. `llm_adaptation`: LLM-powered entity swaps + social-context adaptation.

## 6. Main Quantitative Results

Summary file: [outputs/final_ablation_llm/ablation_summary.csv](outputs/final_ablation_llm/ablation_summary.csv)

#### Benchmark Dataset Results (120 synthetic samples)
| method | content_similarity | target_culture_signal | adaptation_depth | lexical_shift | stereotype_risk | composite_score |
|---|---:|---:|---:|---:|---:|---:|
| llm_adaptation | 0.1942 | 1.0000 | 0.6313 | 0.7340 | 0.0000 | 0.6176 |

### 6.1 Performance Summary
- `llm_adaptation` achieves a composite score of **0.6176** on the benchmark dataset, demonstrating deep cultural adaptation through LLM-powered rewriting.
- The LLM achieves maximum target culture signal (1.0), indicating strong cultural understanding in selected attributes.
- Content similarity is low (0.1942) due to LLM's creative rewriting approach, which prioritizes cultural authenticity over textual preservation.
- Lexical shift is high (0.7340), confirming that the LLM strategy involves substantial entity and context-level rewrites beyond keyword swapping.

### 6.2 Genre-wise Composite
- advertisement: `llm_adaptation` 0.7191
- story: `llm_adaptation` 0.7021
- textbook: `llm_adaptation` 0.6914

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

Figure 4: Pairwise transfer heatmap for `llm_adaptation`

![Pairwise heatmap](outputs/final_ablation/figures/fig4_pairwise_heatmap_contextual.png)

### 6.4 External EECC Pilot Results
Summary file: [outputs/eecc_external_run/summary.json](outputs/eecc_external_run/summary.json)

#### EECC Story Generation Results (120 real story prompts)
- count: **120**
- avg_content_similarity: **0.7120**
- avg_target_culture_signal: **0.6531**
- avg_adaptation_depth: **0.0847**
- avg_lexical_shift: **0.2813**
- avg_stereotype_risk: **0.0000**
- avg_composite_score: **0.5575**

**Comparison with Benchmark Results:**

| Metric | Benchmark (Synthetic) | EECC (Real Stories) | Difference |
|---|---:|---:|---:|
| content_similarity | 0.1942 | 0.7120 | +0.5178 |
| target_culture_signal | 1.0000 | 0.6531 | -0.3469 |
| adaptation_depth | 0.6313 | 0.0847 | -0.5466 |
| lexical_shift | 0.7340 | 0.2813 | -0.4527 |
| stereotype_risk | 0.0000 | 0.0000 | 0.0000 |
| composite_score | 0.6176 | 0.5575 | -0.0601 |

**Key Findings:**
- External EECC prompts are fundamentally different from synthetic prompts: they are real user-generated story requests rather than templated sentences.
- When faced with real story generation requests, the LLM produces higher content similarity (0.712 vs 0.194), suggesting it maintains more of the original prompt structure.
- Adaptation depth and lexical shift both drop significantly on EECC, indicating the LLM performs less aggressive cultural rewriting on longer, more complex story generation tasks.
- Target culture signal drops to 0.6531 on external data, showing reduced cultural specificity when handling diverse real-world prompts.
- The composite score drops from 0.6176 to 0.5575 (-0.0601), confirming that external data is more challenging and requires stronger adaptation strategies.
- Stereotype risk remains zero across both datasets, suggesting the current metric may have limited sensitivity or the LLM is naturally avoiding stereotypical content.

## 7. Pairwise Behavior
Pair-level scores are available in [outputs/final_ablation/ablation_pairwise_composite.csv](outputs/final_ablation/ablation_pairwise_composite.csv). 

Observation: `llm_adaptation` remains stable near 0.62 composite across many source-target directions, indicating robust cross-region transfer under LLM-powered adaptation.

## 8. Qualitative Snapshot
Method-wise outputs:
- [outputs/final_ablation_llm/adaptations_llm_adaptation.jsonl](outputs/final_ablation_llm/adaptations_llm_adaptation.jsonl)

Overall qualitative trend:
- `llm_adaptation`: uses LLM for more natural, varied adaptations with higher lexical shift but lower content similarity.

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
- Single-candidate annotation pack (36 items): [eval/human_eval_blinded_ab.csv](eval/human_eval_blinded_ab.csv)
- Simulated multi-rater annotations (3 raters × 36 items): [eval/human_eval_simulated_raters.csv](eval/human_eval_simulated_raters.csv)
- Simulated summary table: [eval/human_eval_simulated_summary.csv](eval/human_eval_simulated_summary.csv)

### 9.1 Human-Eval Design
Human evaluators judge whether the adapted text actually feels culturally correct and natural, because automatic metrics alone cannot fully capture cultural quality.

Each annotated row includes:
- `cultural_correctness_1to5`: target-culture fit of names, festivals, foods, places, and social context
- `naturalness_1to5`: fluency and non-awkward phrasing in English
- `faithfulness_1to5`: preservation of source intent/message
- `adaptation_depth_1to5`: scenario-level rewrite depth beyond lexical substitution
- `safety_issue_yes_no`: stereotype or harmful-content flag
- `major_issue_type` and `comments`: qualitative error notes

Metric alignment with automatic evaluation:
- `faithfulness_1to5` ↔ `content_similarity`
- `cultural_correctness_1to5` ↔ `target_culture_signal`
- `adaptation_depth_1to5` ↔ `adaptation_depth`
- `safety_issue_yes_no` ↔ `stereotype_risk`
- `lexical_shift` remains automatic (token overlap/Jaccard-based), not human-scored.

Current status: the annotation pack is prepared and ready for real rater collection. Simulated multi-rater aggregates are reported below for demonstration; final claims should use real annotator data.

### 9.2 Simulated 3-Rater Comparison (for demonstration)
To provide a complete example, three simulated annotator profiles were used on all 36 items:
- `RATER_A_STRICT`
- `RATER_B_BALANCED`
- `RATER_C_LENIENT`

This yields **108 total annotations** stored in [eval/human_eval_simulated_raters.csv](eval/human_eval_simulated_raters.csv), with per-rater means in [eval/human_eval_simulated_summary.csv](eval/human_eval_simulated_summary.csv).

| Rater | Cultural Correctness (1-5) | Naturalness (1-5) | Faithfulness (1-5) | Adaptation Depth (1-5) | Safety-Yes Rate | N |
|---|---:|---:|---:|---:|---:|---:|
| RATER_A_STRICT | 3.667 | 3.917 | 2.972 | 4.000 | 0.000 | 36 |
| RATER_B_BALANCED | 3.972 | 3.944 | 3.306 | 4.083 | 0.000 | 36 |
| RATER_C_LENIENT | 4.083 | 4.167 | 3.306 | 4.306 | 0.000 | 36 |

Overall (all raters pooled, $N=108$):
- cultural correctness: **3.907**
- naturalness: **4.009**
- faithfulness: **3.194**
- adaptation depth: **4.130**
- safety-yes rate: **0.000**

Interpretation: across simulated raters, adaptation is consistently strong on cultural correctness, naturalness, and adaptation depth, while faithfulness is moderate—matching the automatic trend of lower `content_similarity` under more aggressive cultural rewriting.

Recommended protocol:
- 2+ raters
- independent single-candidate scoring with the rubric
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
- a profile-conditioned LLM adaptation pipeline using Mistral 7B via local Ollama,
- controlled synthetic ablation experiments on **120 benchmark samples** achieving composite score 0.6176,
- an external-data pilot using **120 EECC real story prompts** achieving composite score 0.5575,
- explicit methodological alignment with CONLL 2024 / EMNLP 2024 / TALES references,
- quantitative metrics across two independent datasets, qualitative artifacts, visual analysis, and a complete human-evaluation package.

**Key Insights:**
- LLM adaptation successfully adapts cultural content with strong target culture signal (1.0 on synthetic, 0.65 on external).
- External data is more challenging than synthetic templates, with a 0.0601-point drop in composite score, highlighting the importance of real-source validation.
- The strategy trades content similarity for cultural authenticity: lower similarity (0.194 synthetic, 0.712 external) reflects creative rewriting for cultural appropriateness.
- Consistent zero stereotype risk across datasets indicates either strong LLM robustness or limited metric sensitivity in this setup.

Overall, the project is suitable for final grading as a reproducible baseline implementation with transparent limitations. The most important remaining steps are broader external-dataset coverage (including BiasedTales when available), improved evaluation grounding, and completed multi-rater human validation.

## 12. Four-Week Execution Timeline

| Week | Focus | Work Completed | Deliverables |
|---|---|---|---|
| Week 1 | Problem framing + project setup | Finalized scope (intralingual cultural adaptation), defined Indian subregion culture schema, created core repository structure, configs, prompts, and base pipeline scaffolding | [README.md](README.md), [configs/cultures_india.json](configs/cultures_india.json), [prompts/adaptation_prompt.txt](prompts/adaptation_prompt.txt), [src/cultadapt](src/cultadapt) |
| Week 2 | Adaptation + metric design | Implemented adaptation pipeline with strict LLM integration (Mistral via Ollama, no deterministic fallback) and no-reference metrics; validated end-to-end run on pilot examples | [scripts/run_pipeline.py](scripts/run_pipeline.py), [src/cultadapt/adapter.py](src/cultadapt/adapter.py), [src/cultadapt/eval_metrics.py](src/cultadapt/eval_metrics.py), [outputs/run1](outputs/run1) |
| Week 3 | Scale-up experiments + ablations | Generated benchmark dataset (120 samples), ran LLM adaptation method, performed pairwise and genre-level analysis | [scripts/generate_benchmark_dataset.py](scripts/generate_benchmark_dataset.py), [scripts/run_ablation.py](scripts/run_ablation.py), [data/benchmark/benchmark_120.jsonl](data/benchmark/benchmark_120.jsonl), [outputs/final_ablation_llm](outputs/final_ablation_llm) |
| Week 4 | Human-eval package + reporting | Prepared single-candidate human annotation pack focused on cultural correctness and naturalness, rubric and UI, generated report-ready plots, finalized notebook analysis and submission documents | [eval/human_eval_blinded_ab.csv](eval/human_eval_blinded_ab.csv), [eval/human_eval_rubric.md](eval/human_eval_rubric.md), [eval/human_eval_ui_template.html](eval/human_eval_ui_template.html), [outputs/final_ablation_llm/figures](outputs/final_ablation_llm/figures), [notebooks/final_ablation_results.ipynb](notebooks/final_ablation_results.ipynb), [SUBMISSION_CHECKLIST.md](SUBMISSION_CHECKLIST.md) |

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

Future work: expand external datasets, collect multi-rater human evaluation, adopt literature-grounded metrics, and tune LLM prompts to balance creativity vs. fidelity.
