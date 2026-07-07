"""Ordinal-scale-only contradiction detection (see ADR-003). Deterministic, no LLM.

Narrative dimensions (incidents, regulations) deliberately have no equivalent here --
a lexical-overlap proxy would launder a semantic judgment as if it were deterministic,
which is worse than no detection at all.
"""

import re

SCALE = ["low", "low-medium", "medium-high", "high", "extremely high"]


def _position_from_text(text: str) -> int | None:
    text_l = text.lower()
    score_match = re.search(r"(\d(?:\.\d)?)\s*/\s*5", text_l)
    if score_match:
        score = float(score_match.group(1))
        return min(4, max(0, round(score) - 1))
    # Check longest labels first: "high" is a substring of "extremely high", so
    # scanning in scale order would match the wrong (shorter) label first.
    for i, label in sorted(enumerate(SCALE), key=lambda pair: -len(pair[1])):
        if label in text_l:
            return i
    return None


def contradicts(claim_a: str, claim_b: str) -> bool | None:
    """Returns True/False if both claims map to the ordinal scale, else None (unknown)."""
    pos_a = _position_from_text(claim_a)
    pos_b = _position_from_text(claim_b)
    if pos_a is None or pos_b is None:
        return None
    return abs(pos_a - pos_b) >= 2
