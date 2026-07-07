# ADR-006: Self-critique relevance check (bonus)

## Status
Accepted

## Context
The committed example run ([`docs/example-output/report.md`](../example-output/report.md))
surfaced a concrete case: a Chandler Incidents source (`abc15.com`) passed deterministic
verification (the excerpt genuinely appears on the page) but the selected chunk was
mostly site-navigation chrome ("Let's Talk Things To Do Operation Safe Roads Smart
Shopper...") with the real article text at the tail end. Verification did its job
correctly — the text is on the page — but nothing in the pipeline judged whether the
selected chunk was actually *good signal* versus incidentally-verifiable boilerplate.
This is the bonus scope item ("AI agents with self-critique capabilities regarding source
relevance") the brief calls out, and this run gave a ready-made acceptance test for it.

## Decision
Add a second, independent LLM call — `critique_relevance` — after a source has already
passed deterministic verification. It reviews the same `{claim, excerpt}` pair `select_chunk`
produced and gives a second opinion on whether the excerpt is *substantively* relevant
(not boilerplate/off-topic/wrong-location), separate from whether it's *verifiably present*
on the page (already settled by ADR-002).

**Critical constraint, consistent with every other failure-handling decision in this
project (ADR-003): a `critique_relevance` disagreement never drops or downgrades a
verified entry.** If `select_chunk` said relevant and verification passed, the source stays
`✅ MATCH FOUND` and counts toward the 2-source minimum, full stop. `critique_relevance`
can only *add* a visible `⚠️ LOW RELEVANCE: <reason>` annotation alongside it. This mirrors
the contradiction-handling principle from ADR-003: transparency over automated resolution.
Silently dropping a verified-but-low-relevance source would mean letting a second, equally
fallible LLM call unilaterally overrule a page fact that's already been mechanically
confirmed to exist — trading one integrity risk (a bad chunk making it into the report) for
another (an LLM veto with no verification step in the loop for its own disagreement).

## Cost
At Sonnet 5 pricing ($2/$10 per MTok input/output, introductory through Aug 2026): each
critique call is ~800-900 input tokens (excerpt + claim + tool-use overhead) and ~80
output tokens, i.e. **~$0.0025 per verified source**. At demo scale (3 locations × 3
dimensions × ~2 verified sources) this is ~$0.05 total; at 1,000-location scale
(~6,000 verified sources) it's roughly $15-20 — trivial next to the `web_search` tool's
own $10/1,000-search fee at that scale. The real cost was engineering time (~30-45 min),
not API spend, which is why this was picked up as in-budget bonus scope rather than
deferred.

## Consequences
- Every verified source now costs one additional LLM call (`_llm_sem`-gated, same
  concurrency discipline as discovery/extraction — see ADR-004).
- `SourceResult` gained `low_relevance: bool` and `critique_reason: str`, surfaced in both
  the Markdown report and the CSV bonus output.
- This does not replace deterministic verification (ADR-002) as the pass/fail gate — it's
  a visibility layer on top of already-verified data, never a substitute for it.
