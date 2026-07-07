# ADR-002: Verification is deterministic code, never the LLM

## Status
Accepted

## Context
Brief requirement: "The script must fetch the URL and verify that the provided 'Excerpt'
actually exists within the page content." This is the pass/fail gate the whole exercise is
graded on ("Data Integrity: methods to avoid AI hallucinations").

## Decision
Verification is a pure function: `normalize(excerpt) in normalize(page_text)`, executed in
plain Python, with zero model calls. No LLM is ever asked "does this excerpt match" or
"is this close enough" — that would mean trusting the same class of system that produces
hallucinations to grade its own output.

Normalization is intentionally minimal and documented, not tunable per-call:
- Unicode NFKC normalization (smart quotes, non-breaking spaces → standard forms)
- Whitespace collapse (newlines/tabs/multiple spaces → single space)
- Case-insensitive comparison

No fuzzy/similarity-threshold matching is implemented. A fuzzy threshold is itself an
undocumented judgment call about how much divergence from the source to tolerate, which
directly contradicts "traceability is absolute priority." If normalized exact match fails,
the result is `❌ ERROR: Text excerpt not found in source content` — full stop, no partial
credit state invented beyond what the brief's own example shows (`✅ MATCH FOUND` /
`❌ ERROR`).

## Consequences
- Some false negatives are possible if a source page is edited between crawl and verify,
  or has genuinely unusual encoding. This is accepted as the safer failure mode: a false
  `[FAILED VALIDATION]` costs a re-run; a false pass costs trust in the whole report.
- Combined with ADR-001 (verbatim chunk extraction), false negatives from LLM paraphrasing
  are structurally eliminated, so the residual false-negative rate from normalization edge
  cases alone should be small.
