# ADR-001: Extraction is retrieval, not generation

## Status
Accepted

## Context
The brief states quality/accuracy/traceability are Waterplan's "absolute priority" and
requires the tool to "validate via software that each data point is faithfully supported
by its original source." The single biggest risk to that is an LLM asked to produce an
"excerpt" instead **paraphrasing** the source — which then either (a) fails a strict
verbatim check as a false negative, or (b) passes a fuzzy check as a false positive that
launders a hallucination as verified fact.

## Decision
The LLM never authors the excerpt text. The pipeline:
1. Fetches the raw page text (see ADR-005 for fetch strategy).
2. Splits it into indexed chunks (paragraph-bounded, ~500-1000 chars).
3. Asks the LLM, via forced tool-calling, to return `{chunk_index, data}` — i.e. *which
   chunk* supports the claim, plus a short interpretive summary (`data`).
4. The code — not the model — pulls the literal chunk text at that index and uses it as
   the `Excerpt`.
5. Verification (ADR-002) re-checks that literal text is still a genuine substring of the
   freshly normalized page text.

The model is never in a position to type out prose that becomes the "ground truth"
excerpt. It can only point at a location in text that was independently fetched.

## Consequences
- `Data` (the short claim, e.g. "Extremely High water stress (score 4.8/5)") is still
  LLM-authored and may be a paraphrase — that's fine, it's clearly presented as
  interpretation, and the reader can check it against the verbatim `Excerpt` next to it.
- `Excerpt` can never diverge from the source by construction, only by chunk-index error,
  which ADR-002's re-verification step catches.
- Slightly more engineering (chunking, index mapping) than "ask the model to quote the
  source," which was rejected — it relies entirely on prompt discipline and still permits
  a paraphrased "verbatim" quote to slip through a strict-match check.
