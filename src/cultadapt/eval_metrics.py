from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict, List

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


@dataclass
class MetricWeights:
    content_similarity: float = 0.35
    target_culture_signal: float = 0.25
    adaptation_depth: float = 0.20
    lexical_shift: float = 0.10
    stereotype_safety: float = 0.10


def evaluate_pair(
    source_text: str,
    adapted_text: str,
    source_profile: Dict,
    target_profile: Dict,
    weights: MetricWeights | None = None,
) -> Dict[str, float]:
    weights = weights or MetricWeights()

    content = content_similarity(source_text, adapted_text)
    tgt_signal = target_culture_signal(adapted_text, source_profile, target_profile)
    depth = adaptation_depth(source_text, adapted_text, source_profile, target_profile)
    shift = lexical_shift(source_text, adapted_text)
    risk = stereotype_risk(adapted_text)
    safety = 1.0 - risk

    composite = (
        weights.content_similarity * content
        + weights.target_culture_signal * tgt_signal
        + weights.adaptation_depth * depth
        + weights.lexical_shift * shift
        + weights.stereotype_safety * safety
    )

    return {
        "content_similarity": round(float(content), 4),
        "target_culture_signal": round(float(tgt_signal), 4),
        "adaptation_depth": round(float(depth), 4),
        "lexical_shift": round(float(shift), 4),
        "stereotype_risk": round(float(risk), 4),
        "composite_score": round(float(composite), 4),
    }


def content_similarity(a: str, b: str) -> float:
    if not a.strip() or not b.strip():
        return 0.0
    vec = TfidfVectorizer(ngram_range=(1, 2), min_df=1)
    mat = vec.fit_transform([a, b])
    score = cosine_similarity(mat[0], mat[1])[0, 0]
    return float(np.clip(score, 0.0, 1.0))


def target_culture_signal(text: str, source_profile: Dict, target_profile: Dict) -> float:
    t_hits = _profile_hits(text, target_profile)
    s_hits = _profile_hits(text, source_profile)
    total = max(1, _token_count(text))

    raw = (t_hits - 0.4 * s_hits) / total * 20.0
    return float(np.clip(raw, 0.0, 1.0))


def adaptation_depth(source_text: str, adapted_text: str, source_profile: Dict, target_profile: Dict) -> float:
    dimensions = ["names", "foods", "festivals", "places", "social_context", "tone_cues"]
    changed = 0
    for d in dimensions:
        src_terms = source_profile.get(d, [])
        tgt_terms = target_profile.get(d, [])
        src_in_source = _contains_any(source_text, src_terms)
        src_in_adapted = _contains_any(adapted_text, src_terms)
        tgt_in_adapted = _contains_any(adapted_text, tgt_terms)

        if src_in_source and (not src_in_adapted) and tgt_in_adapted:
            changed += 1
        elif (not src_in_source) and tgt_in_adapted:
            changed += 0.5

    return float(np.clip(changed / len(dimensions), 0.0, 1.0))


def lexical_shift(source_text: str, adapted_text: str) -> float:
    a = set(_normalize_tokens(source_text))
    b = set(_normalize_tokens(adapted_text))
    if not a or not b:
        return 0.0
    jaccard = len(a & b) / len(a | b)
    return float(np.clip(1.0 - jaccard, 0.0, 1.0))


def stereotype_risk(text: str) -> float:
    patterns = [
        r"\b(all|every|typical)\s+[a-z\-\s]+\s+(are|is)\b",
        r"\bbackward\b",
        r"\bprimitive\b",
        r"\buncivilized\b",
        r"\bexotic\b",
    ]
    lowered = text.lower()
    matches = sum(1 for p in patterns if re.search(p, lowered))
    return float(np.clip(matches / 3.0, 0.0, 1.0))


def _profile_hits(text: str, profile: Dict) -> int:
    fields = ["names", "foods", "festivals", "places", "social_context", "tone_cues", "languages"]
    return sum(_count_matches(text, profile.get(f, [])) for f in fields)


def _count_matches(text: str, terms: List[str]) -> int:
    c = 0
    for term in terms:
        c += len(re.findall(rf"\b{re.escape(term.lower())}\b", text.lower()))
    return c


def _contains_any(text: str, terms: List[str]) -> bool:
    t = text.lower()
    return any(re.search(rf"\b{re.escape(x.lower())}\b", t) for x in terms)


def _token_count(text: str) -> int:
    return len(_normalize_tokens(text))


def _normalize_tokens(text: str) -> List[str]:
    return re.findall(r"[a-zA-Z]+", text.lower())
