# ADR-003: Failure handling, minimum sourcing, and contradictions

## Status
Accepted

## Context
Brief requires ≥2 sources per researched item, and clear flagging when a URL is down or
an excerpt doesn't match. Neither the brief nor common sense specifies what to do when
sourcing falls short, or when two verified sources disagree.

## Decisions

### Minimum sourcing: retry-until-satisfied, capped, then transparent
For each (location, dimension), discovery is retried with new **distinct candidate URLs**
(not refetches of the same URL) up to a cap of 5 distinct candidates, stopping early once
2 are verified. If fewer than 2 verified sources exist after exhausting the cap, the
dimension is still reported — never omitted — flagged as:

`⚠️ INSUFFICIENT SOURCES (n/2 verified)`

Rejected alternative: omitting the dimension when <2 sources verify. Silently dropping a
dimension because data was hard to find is a worse failure mode than showing a smaller
result honestly labeled — it hides effort and hides risk from the reader, when the entire
point of the tool is to surface risk.

### Failed candidates are shown, not hidden
A candidate URL that fails fetch or fails verification is still listed in the report under
that dimension with `[FAILED VALIDATION]` and a reason (`fetch_error`, `excerpt_mismatch`).
This gives the reader an audit trail of what was tried, not just what succeeded.

### Contradictions between verified sources
No automated reconciliation is performed anywhere — the tool never picks a "winner"
between two verified-but-disagreeing sources. Both are always shown side-by-side.

Automated **contradiction flagging** (an `ℹ️ Note: sources disagree` annotation) is
implemented *only* for the Water Stress dimension, because it is the one dimension backed
by a standardized ordinal scale (e.g. WRI Aqueduct 0-5 score / Low..Extremely High
categories). Rule, computed in code with no model involved:
- Map each verified source's claim to a scale position.
- Adjacent or equal positions (|Δ| ≤ 1) → aligned, no note.
- |Δ| ≥ 2 → `ℹ️ Note: sources disagree`.

For Incidents and Regulations (free-text/narrative dimensions), **no automated
contradiction detection is attempted**, including no lexical/keyword-overlap proxy. A
lexical overlap score measures shared vocabulary, not agreement — two directly opposite
narrative claims ("protests occurred" vs. "no protests occurred") can score high overlap,
which would make the proxy worse than no detection at all: it dresses up an unverified
semantic judgment as if it were deterministic. This is a deliberate, documented scope
boundary, not a gap to fill later with more time.

## Consequences
- The report is always complete (every dimension present for every location) and always
  honest about confidence (flags visible wherever sourcing or agreement is weak).
- Contradiction detection coverage is narrower than "ideal" but everything it does report
  is fully auditable and machine-checked; nothing is claimed that isn't backed by code.
