# Example output history

Real, unedited runs of the tool, kept as a history rather than a single overwritten file —
each run demonstrates something different and stays valid evidence even after later runs
supersede it in other ways.

- [`run-01-blocklist-fix/report.md`](run-01-blocklist-fix/report.md) — first run after the
  water-stress domain blocklist fix (ADR-003). Predates the self-critique check; shows the
  `abc15.com` boilerplate case that motivated building it.
- [`run-02-self-critique/report.md`](run-02-self-critique/report.md) — later run with the
  self-critique relevance check (ADR-006) live, catching three distinct real
  verified-but-not-actually-relevant cases.
- [`run-03-haiku-comparison/report.md`](run-03-haiku-comparison/report.md) — same
  pipeline and locations as run-02, with `CLAUDE_MODEL` switched to the cheaper Haiku 4.5.
  Shows a real cost/quality trade-off: the self-critique check produced zero flags
  (including on the case it caught with Sonnet in run-02), and Water Stress sourcing
  yield dropped for two of three locations.

Each file has its own "how to read this report" legend and is self-contained.
