# ADR-005: Stack choice — Python, Anthropic, tiered fetch

## Status
Accepted

## Runtime: Python
Brief permits Python, Node.js, or Go. Python chosen because:
- None of the five graded axes (architecture, robustness, data integrity, scalability,
  failure handling) reward raw runtime performance specifically.
- Richest, most mature ecosystem for the actual needs here: Anthropic SDK, `httpx`
  (async), Playwright (first-class Python API).
- Fastest path to a clean, idiomatic result within the 24h timebox.

**Go considered and rejected**: would be the more "impressive" choice for a role that
implies production/scale thinking, but optimizes an attribute (I/O throughput) that isn't
measured by this exercise, at real risk to the timebox given less mature LLM SDK ergonomics.
Revisit if I/O throughput becomes the actual bottleneck at real 1000+ location scale
(see ADR-004).

## LLM provider: Anthropic, behind a thin interface
Anthropic chosen for the actual implementation (API access available, fits the framing of
a company already in this ecosystem). The task itself (chunk-index selection via forced
tool-calling — see ADR-001) is narrow, structured-output-heavy, and roughly
provider-equivalent in difficulty; this is a lighter decision than the runtime choice.

To avoid hard-wiring to one vendor, extraction is called through a thin `LLMClient`
interface with a single method:

```python
def select_chunk(chunks: list[str], claim_context: str) -> dict:
    """Returns {"chunk_index": int, "data": str} via forced tool-calling."""
```

Swapping providers means implementing this interface — a design decision documented here,
not something built as multi-provider support in this 24h window.

**Ollama / local models explicitly rejected**, even as a documented option. ADR-001's
entire integrity design depends on reliable structured/tool-call output at exactly the
step (`chunk_index` selection) where a hallucination would be most damaging. A weaker
model risks failing at that critical point for a cost saving (a few cents across a
handful of locations) that isn't worth the risk.

## Discovery: Anthropic's `web_search` tool, not a separate search API
Verified against current Anthropic API docs: `web_search_tool_result` content blocks
return structured `web_search_result` objects with a plain `url` field per result,
extractable in code before any model prose — so raw candidate URLs are available
independent of the model's summarization.

Using the same provider for discovery removes an entire external dependency (no separate
search API signup/key). This doesn't violate the "no LLM in the verdict" boundary from
ADR-001/002: the model is only producing a list of candidate URLs, every one of which
still goes through independent fetch + verify. Discovery quality being imperfect is
already handled honestly by ADR-003's INSUFFICIENT SOURCES flow.

## Fetch: tiered static → optional headless, reproducibility over completeness
- **Default path** (no extra runtime deps): static HTTP fetch (`httpx`) + HTML text
  extraction. Works everywhere, zero setup risk for whoever runs the tool.
- **Optional headless fallback** (Playwright): real code, gated behind an optional
  import. If unavailable, the tool logs `[INFO] Headless fallback unavailable` and
  proceeds to `[FAILED VALIDATION: fetch blocked]` rather than crashing.
- **Optional Docker image**: bakes in Playwright + browser binaries for anyone who wants
  the full tiered fetch (static → headless) fully reproducibly, without requiring it to
  evaluate the core deliverable.

Rejected: requiring Playwright unconditionally — browser binary installs are a real
reproducibility risk in an unknown reviewer environment, and the brief's core ask (excerpt
verification against fetched content) doesn't require it to be graded.
