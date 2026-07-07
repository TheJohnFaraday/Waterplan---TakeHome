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
2. Splits it into indexed chunks: a fixed-size sliding window (800 chars, 100-char
   overlap between consecutive chunks — see `verify.chunk_text`), not paragraph-aware.
   A chunk can start or end mid-sentence; the overlap exists so a claim sitting on a
   chunk boundary is still likely to appear whole in at least one chunk.
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
- Because chunking is fixed-size and not paragraph/sentence-aware, reported excerpts
  routinely start or end mid-word (visible throughout `docs/example-output/report.md`,
  e.g. `"...ent to help mitigate the crisis..."`). This is a readability cost, not an
  integrity one — the excerpt is still a genuine, verified substring of the source; it's
  just not trimmed to clean sentence boundaries. Fixing this (sentence-aware chunking)
  is a UX polish item, not a correctness one, and was left out of this timebox.
