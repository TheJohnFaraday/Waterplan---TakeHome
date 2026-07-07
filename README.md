# Waterplan Water Risk Research Tool

Automates water-risk research for a list of locations across three dimensions (water
stress, incidents/conflicts, regulations), with every reported data point independently
and deterministically verified against its cited source. Design rationale and trade-offs
are documented as ADRs in [`docs/adr/`](docs/adr/) — start there for the "why."

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
report (Markdown + CSV)
```

- **ADR-001**: the LLM never authors the excerpt text — it only points at a chunk index
  in independently fetched text; code extracts the literal excerpt.
- **ADR-002**: verification is a pure function, no model in the pass/fail decision.
- **ADR-003**: minimum-sourcing retry policy, failure flagging, and the ordinal-only
  contradiction detection rule.
- **ADR-004**: how this scales to 1000 locations (decoupled backpressure now; queue-based
  workers as documented future evolution).
- **ADR-005**: stack choice (Python, Anthropic, tiered fetch) and alternatives rejected.

## Known limitations (documented scope boundaries, not gaps)

- Contradiction detection only covers the Water Stress dimension (ordinal scale). No
  automated contradiction detection for Incidents/Regulations (narrative text) — see
  ADR-003 for why a lexical-overlap proxy was rejected rather than built.
- Self-critique agent (source-relevance bonus) not built in this pass — flagged as
  remaining stretch scope dependent on time budget.
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
Dockerfile               Optional full-fetch reproducible environment
```