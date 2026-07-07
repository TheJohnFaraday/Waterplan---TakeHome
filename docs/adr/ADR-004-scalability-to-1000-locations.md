# ADR-004: Scalability to 1000 locations

## Status
Accepted

## Context
Brief evaluates "how you would adapt this flow to process 1,000 locations efficiently."
At 1000 locations × 3 dimensions × up to 5 candidate fetches, this is 15,000+ fetch+verify
operations plus a comparable number of LLM calls (discovery + chunk-selection), against
two different rate limits (Anthropic's API, and per-domain politeness/bot-detection
limits on arbitrary third-party sites).

## Decision: async I/O now, queue-based architecture as documented evolution

### What is actually built (this repo, demo scale)
Bounded-concurrency `asyncio`, with **two independent semaphores**, not one global limit:
- LLM semaphore (bounds concurrent Anthropic calls — this is the backpressure point
  against Anthropic's own rate limits, tokens/min and requests/min).
- Fetch semaphore, further scoped **per-domain** (bounds concurrent requests to any single
  site — this is the backpressure point against bot detection / politeness, independent
  of how many locations are in flight globally).

These are deliberately decoupled: the LLM stage and the fetch stage are rate-limited by
different external systems, so a single shared concurrency limit would either starve one
stage or exceed the other's tolerance.

### What is documented, not built, for real 1000+ scale production use
- **Queue-based workers** (e.g. Celery/RQ + Redis, or a cloud task queue): each
  (location, dimension) unit of work becomes an independent, retryable job. This
  decouples "how many locations" from "how many processes," and allows horizontal scaling
  across machines rather than one process's asyncio event loop.
- **Idempotency**: each job is keyed by `(location, dimension, candidate_url)`; re-running
  the pipeline (e.g. after a partial failure) must not re-verify or re-report work already
  completed and cached (see caching below). This makes runs safely resumable.
- **Fault isolation**: a failure processing location #742 must not affect the other 999 —
  already true in the async model (per-task exception handling), and remains true in a
  queue model (a failed job doesn't block or crash other queued jobs).
- **Per-domain rate limiting at scale**: with 1000 locations, some domains (e.g. WRI
  Aqueduct, government portals) will be hit far more often than others. Production-scale
  per-domain limits and possibly a shared token-bucket across workers would be needed
  where the async model's in-process semaphore is not (Redis-backed rate limiter).
- **Runtime choice reconsidered**: Python was chosen for this deliverable (ADR-005) because
  none of the five graded axes reward raw throughput. If I/O throughput became the actual
  bottleneck at real 1000+ location production scale, Go's lighter-weight concurrency
  primitives would be worth revisiting — but that's a decision to make once real load data
  exists, not up front.

## Consequences
- The demo code demonstrates the *pattern* (decoupled backpressure, bounded concurrency)
  at a scale (3 locations) too small to prove it matters — this ADR is where the
  reasoning for 1000-location scale actually lives, since building the full queue infra
  for a 24h take-home would be scope well beyond "understand your thought process."
