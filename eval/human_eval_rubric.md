# Human Evaluation Rubric (Indian Subregion Cultural Adaptation)

## Scale
Use 1–5 for each metric:
- 1 = very poor
- 2 = poor
- 3 = acceptable
- 4 = good
- 5 = excellent

## Dimensions
1. **Authenticity**: How naturally the adapted text fits the target culture.
2. **Faithfulness**: How well core meaning and intent from the source are preserved.
3. **Coherence**: Fluency, logical flow, readability.
4. **Safety**: Avoids stereotypes, disrespect, caricature.
5. **Adaptation Depth**: Goes beyond word swaps; context and scenario are adapted.
6. **Overall Preference**: Holistic quality judgment.

## Annotation Notes
- Do not penalize minor style differences if meaning is preserved.
- Penalize shallow lexical substitution with no scenario adaptation.
- Penalize fabricated or offensive cultural claims.
- Use `major_issue_type` with one of: `none`, `shallow_swap`, `over_localization`, `stereotype`, `factual_mismatch`, `other`.

## Agreement Protocol
- At least 2 annotators per sample.
- Resolve large disagreement (|score_a - score_b| >= 2) with adjudication.
