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

## Observed finding: Water Stress systematically under-sources against dashboard-style domains

A live run against the brief's three example locations showed Water Stress reaching
`INSUFFICIENT SOURCES` on all three, while Incidents and Regulations consistently reached
2+ verified sources. Every failing candidate came from the same handful of domains:
`wri.org/applications/aqueduct/...`, `resourcewatch.org`, `esri.com`. These are
interactive map/dashboard applications — their static HTML is mostly JS app shell and UI
chrome, with the actual per-location score rendered client-side and never present in the
fetched text. `select_chunk` correctly returned `relevant: false` rather than fabricating
a score from UI boilerplate — this is the pipeline behaving exactly as designed (ADR-001:
abstain rather than hallucinate), not a bug in extraction or verification. The one Water
Stress source that *did* verify (a news article citing the Aqueduct score in prose) shows
the pattern clearly: narrative/reported summaries of dashboard data are scrapeable,
the dashboards themselves generally are not.

### Mitigation: domain blocklist (`WATER_STRESS_BLOCKED_DOMAINS` in `config.py`)
The three known-bad domains are passed as `blocked_domains` on the `web_search` tool call
for the Water Stress query, so discovery stops surfacing them as candidates at all. This
is applied before search, not a retry/iteration loop, so it costs nothing extra per run.

**This is explicitly a mitigation, not a fix, and is documented as a known limitation
rather than oversold:** it only excludes the *specific* dashboard domains already observed
to fail. Any unseen dashboard-style domain (a different country's water-risk portal, a
different GIS tool, etc.) would hit the same failure mode and would need to be added to
the blocklist manually after being observed — there is no general detector here for
"this page is a JS dashboard with no scrapeable per-location text." A more complete fix
(e.g. detecting thin/app-shell content heuristically, or querying such dashboards' actual
backing data APIs where available) is out of scope for this timebox and would need to be
built dimension-by-dimension as new sources are encountered at real usage scale.

### Test coverage caught a real ordering bug in the ordinal scale matcher
`tests/test_contradictions.py` covers `_position_from_text`'s label-matching branch. A test
for `"Extremely High"` failed against the original implementation: `SCALE` is checked in
ascending order, and `"high"` (index 3) is a substring of `"extremely high"`, so
`"extremely high risk"` matched `"high"` first and was silently mapped to position 3
instead of 4. Fixed by matching the longest label first. Kept as a concrete case for why
the deterministic modules have unit tests even though the take-home didn't require them —
this bug would have made the contradiction check systematically too lenient (treating a
real Low-vs-Extremely-High contradiction as only |Δ|=1) with no visible symptom in a normal
run.
