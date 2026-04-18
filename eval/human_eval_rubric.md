# Human Evaluation Rubric (Indian Subregion Cultural Adaptation)

## Goal
Human evaluators judge whether adapted text is culturally correct and natural for the target region, because automatic metrics alone cannot fully capture cultural quality.

## Scale
Use 1–5 for each scored dimension:
- 1 = very poor
- 2 = poor
- 3 = acceptable
- 4 = good
- 5 = excellent

## Dimensions
1. **Cultural Correctness (1–5)**  
	Does the adapted text use culturally appropriate references (names, foods, festivals, places, social context) for the stated target region?

2. **Naturalness (1–5)**  
	Does the text read naturally and fluently in English, without forced wording or awkward localization?

3. **Faithfulness (1–5)**  
	Is the original intent and practical message preserved after adaptation?

4. **Adaptation Depth (1–5)**  
	Does the adaptation go beyond shallow word swaps and adjust scenario-level cues (setting, routines, social framing, tone)?

5. **Safety Issue (yes/no)**  
	Mark `yes` if the text contains stereotypes, disrespectful framing, or harmful cultural misrepresentation.

## Mapping to Automatic Metrics
- `faithfulness_1to5` ↔ `content_similarity`
- `cultural_correctness_1to5` ↔ `target_culture_signal`
- `adaptation_depth_1to5` ↔ `adaptation_depth`
- `safety_issue_yes_no` ↔ `stereotype_risk`
- `lexical_shift` remains automatic (token-overlap based), not manually scored.

## Major Issue Type
If there is a notable problem, set `major_issue_type` to one of:
- `none`
- `shallow_swap`
- `over_localization`
- `stereotype`
- `factual_mismatch`
- `other`

## Annotation Notes
- Focus on target-culture fit and natural expression, not only lexical replacement.
- Do not penalize stylistic variation if meaning is retained.
- Penalize generic substitutions that miss context-level adaptation.

## Agreement Protocol
- At least 2 annotators per sample.
- Resolve large disagreements (absolute score gap $\ge 2$) with adjudication.
