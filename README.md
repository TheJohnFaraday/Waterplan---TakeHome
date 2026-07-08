# Waterplan Water Risk Research Tool

Automates water-risk research for a list of locations across three dimensions (water
stress, incidents/conflicts, regulations), with every reported data point independently
and deterministically verified against its cited source. Design rationale and trade-offs
are documented as ADRs in [`docs/adr/`](docs/adr/) — start there for the "why." Real,
unedited runs are committed at
[`docs/example-output/`](docs/example-output/README.md) if you want to see results
without running anything yourself.

## Quickstart

```bash
pip install -r requirements.txt
cp .env.example .env   # then edit .env and set your ANTHROPIC_API_KEY
python main.py
```

(Alternatively, skip the `.env` file and just `export ANTHROPIC_API_KEY=sk-ant-...` —
either is picked up automatically.)

Runs the three example locations from the brief (Mexicali, Monterrey, Chandler) and
writes `output/report.md` (Markdown) and `output/report.csv` (consolidated CSV, bonus
scope), printing the Markdown report to stdout as well.

Custom locations:
```bash
python main.py --locations "Bogotá, Colombia" "Phoenix, Arizona, USA"
```

### Configuration

`ANTHROPIC_API_KEY` is the only required setting. Everything else is a deployment knob
with a working default, overridable via `.env` (see `.env.example`) without touching code:

| Env var | Default | What it controls |
|---|---|---|
| `CLAUDE_MODEL` | `claude-sonnet-5` | Model used for discovery, extraction, and self-critique |
| `LLM_CONCURRENCY` | `4` | Max concurrent Anthropic API calls |
| `FETCH_CONCURRENCY_PER_DOMAIN` | `2` | Max concurrent fetches to the same domain |
| `FETCH_CONCURRENCY_GLOBAL` | `10` | Max concurrent fetches overall |
| `CACHE_DIR` | `.cache` | Disk cache location (ADR bonus scope) |
| `OUTPUT_DIR` | `output` | Default report output directory |

Design decisions tied to a specific ADR (chunk size/overlap, retry caps, the water-stress
domain blocklist, dimension definitions) stay as code constants in `config.py` on purpose
— those are trade-offs made once and documented, not meant to be casually overridden per
environment.

## Unit tests

The two deterministic, LLM-free modules (`verify.py`, `contradictions.py` — ADR-002,
ADR-003) have a unit test suite, no API key required:

```bash
python -m unittest discover -s tests -v
```

## Optional: full headless-fetch support via Docker

The default path above works with zero extra setup, using static HTTP fetch only. Some
real-world sources are JS-rendered or bot-blocked and need a headless browser
(Playwright) to fetch. Rather than requiring that dependency unconditionally (a
reproducibility risk in an unknown environment — see ADR-005), it's offered as an
optional path:

```bash
docker build -t waterplan-tool .
docker run --rm -e ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY waterplan-tool
```

Without Docker, `pip install playwright && playwright install chromium` also enables it
locally — the tool detects Playwright's availability automatically and logs when the
headless fallback isn't available rather than failing.

## Architecture (see ADRs for full rationale)

```
discover_urls (Anthropic web_search)   -- ADR-005
        v
fetch (static -> optional headless)     -- ADR-005
        v
chunk + select_chunk (LLM picks index)  -- ADR-001 (retrieval, not generation)
        v
verify_excerpt (deterministic substring match, no LLM)  -- ADR-002
        v
critique_relevance (second-opinion LLM call, verified sources only)  -- ADR-006
        v
report (Markdown + CSV)
```

- **ADR-001**: the LLM never authors the excerpt text — it only points at a chunk index
  in independently fetched text; code extracts the literal excerpt. Trade-off: this rules
  out paraphrased or summarized excerpts entirely, even correct ones — chosen because a
  model that can paraphrase can also hallucinate, and there's no cheap way to tell those
  apart after the fact.
- **ADR-002**: verification is a pure function, no model in the pass/fail decision.
  Trade-off: exact (normalized) substring match has false negatives — a real, true claim
  phrased slightly differently than the source text fails validation — but the alternative
  (fuzzy/semantic matching) reintroduces a judgment call exactly where the anti-hallucination
  guarantee needs to be strongest.
- **ADR-003**: minimum-sourcing retry policy, failure flagging, and the ordinal-only
  contradiction detection rule. Trade-off: contradiction detection only covers the one
  dimension (water stress) with a standardized scale; narrative dimensions get no automated
  detection rather than an unreliable lexical-overlap proxy — an honest gap over a fake
  signal.
- **ADR-004**: how this scales to 1000 locations (decoupled backpressure now; queue-based
  workers as documented future evolution). Trade-off: not built for this submission — the
  brief's example scope is 3 locations, and building unused infrastructure would cost time
  better spent hardening what's graded.
- **ADR-005**: stack choice (Python, Anthropic, tiered fetch) and alternatives rejected.
  Trade-off: Python over Go/Node because none of the five eval axes reward raw runtime
  throughput; Anthropic over a separate search API because `web_search` returns citable
  URLs directly, one fewer moving part and one fewer credential to manage.
- **ADR-006**: self-critique relevance check (bonus) — a second LLM opinion on already-
  verified sources, surfaced as an additive `⚠️ LOW RELEVANCE` flag, never a silent drop
  or downgrade of a verified entry. Trade-off: costs a second LLM call per verified source
  (~$0.0025 each) purely for a soft signal a human still has to read — accepted because
  silently trusting "verified" as "relevant" was the actual gap it closes (see the
  `abc15.com` case in `docs/example-output/`).

## Known limitations (documented scope boundaries, not gaps)

- Contradiction detection only covers the Water Stress dimension (ordinal scale). No
  automated contradiction detection for Incidents/Regulations (narrative text) — see
  ADR-003 for why a lexical-overlap proxy was rejected rather than built.
- Headless fetch fallback requires optional Playwright install or Docker; without either,
  bot-blocked/JS-rendered sources fail cleanly as `[FAILED VALIDATION]`.

## Repo layout

```
main.py                  CLI entrypoint
src/waterplan/
  config.py              Dimensions, locations, tunables
  llm_client.py           Thin LLMClient interface + Anthropic implementation
  fetcher.py             Tiered static/headless fetch + cache-aware
  cache.py                Disk cache keyed by URL (bonus scope)
  verify.py               Deterministic excerpt verification + chunking
  contradictions.py       Ordinal-scale-only contradiction rule
  pipeline.py             Orchestration (discovery -> fetch -> extract -> verify)
  report.py               Markdown + CSV rendering
docs/adr/                Architecture Decision Records
tests/                  Unit tests for verify.py and contradictions.py (no API key needed)
Dockerfile               Optional full-fetch reproducible environment
```