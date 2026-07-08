"""Orchestration: discovery -> fetch -> extract (retrieval) -> verify (see ADRs 001-004)."""

import asyncio
import logging
from dataclasses import dataclass, field

from waterplan import config
from waterplan.cache import FetchCache
from waterplan.contradictions import contradicts
from waterplan.fetcher import Fetcher
from waterplan.llm_client import LLMClient
from waterplan.verify import chunk_text, verify_excerpt

logger = logging.getLogger(__name__)


@dataclass
class SourceResult:
    url: str
    verified: bool
    data: str = ""
    excerpt: str = ""
    error: str = ""
    low_relevance: bool = False
    critique_reason: str = ""


@dataclass
class DimensionResult:
    dimension_key: str
    dimension_label: str
    emoji: str
    sources: list[SourceResult] = field(default_factory=list)
    failed_candidates: list[SourceResult] = field(default_factory=list)
    contradiction_note: bool = False

    @property
    def verified_count(self) -> int:
        return sum(1 for s in self.sources if s.verified)

    @property
    def insufficient(self) -> bool:
        return self.verified_count < config.MIN_VERIFIED_SOURCES


@dataclass
class LocationResult:
    location: str
    dimensions: list[DimensionResult] = field(default_factory=list)


class Pipeline:
    def __init__(self, llm: LLMClient, cache_dir: str = config.CACHE_DIR):
        self.llm = llm
        self.fetcher = Fetcher(
            FetchCache(cache_dir),
            global_concurrency=config.FETCH_CONCURRENCY_GLOBAL,
            per_domain_concurrency=config.FETCH_CONCURRENCY_PER_DOMAIN,
        )
        self._llm_sem = asyncio.Semaphore(config.LLM_CONCURRENCY)

    async def run(self, locations: list[str]) -> list[LocationResult]:
        tasks = [self._process_location(loc) for loc in locations]
        return await asyncio.gather(*tasks)

    async def _process_location(self, location: str) -> LocationResult:
        dim_tasks = [self._process_dimension(location, dim) for dim in config.DIMENSIONS]
        dims = await asyncio.gather(*dim_tasks)
        return LocationResult(location=location, dimensions=list(dims))

    async def _process_dimension(self, location: str, dim: config.Dimension) -> DimensionResult:
        result = DimensionResult(dimension_key=dim.key, dimension_label=dim.label, emoji=dim.emoji)
        query = dim.search_query_template.format(location=location)

        logger.info("[%s] %s: searching (%r)", location, dim.label, query)
        async with self._llm_sem:
            candidates = await asyncio.to_thread(
                self.llm.discover_urls, query, config.WEB_SEARCH_MAX_USES, dim.blocked_domains
            )
        logger.info("[%s] %s: %d candidate URL(s) found", location, dim.label, len(candidates))

        tried = 0
        for candidate in candidates:
            if result.verified_count >= config.MIN_VERIFIED_SOURCES:
                break
            if tried >= config.MAX_CANDIDATE_URLS_PER_DIMENSION:
                break
            tried += 1

            logger.info(
                "[%s] %s: trying candidate %d/%d -> %s",
                location, dim.label, tried, config.MAX_CANDIDATE_URLS_PER_DIMENSION, candidate["url"],
            )
            source = await self._process_candidate(location, dim, candidate["url"])
            if source.verified:
                result.sources.append(source)
                if source.low_relevance:
                    logger.info(
                        "[%s] %s: MATCH FOUND but LOW RELEVANCE (%s) (%d/%d verified)",
                        location, dim.label, source.critique_reason,
                        result.verified_count, config.MIN_VERIFIED_SOURCES,
                    )
                else:
                    logger.info(
                        "[%s] %s: MATCH FOUND (%d/%d verified)",
                        location, dim.label, result.verified_count, config.MIN_VERIFIED_SOURCES,
                    )
            else:
                result.failed_candidates.append(source)
                logger.info("[%s] %s: FAILED VALIDATION (%s)", location, dim.label, source.error)

        if dim.ordinal and result.verified_count >= 2:
            claims = [s.data for s in result.sources if s.verified]
            for i in range(len(claims)):
                for j in range(i + 1, len(claims)):
                    if contradicts(claims[i], claims[j]):
                        result.contradiction_note = True

        return result

    async def _process_candidate(
        self, location: str, dim: config.Dimension, url: str
    ) -> SourceResult:
        fetch_result = await self.fetcher.fetch(url)
        if not fetch_result.ok:
            return SourceResult(url=url, verified=False, error=fetch_result.error or "fetch_failed")

        chunks = chunk_text(fetch_result.text, config.CHUNK_SIZE_CHARS, config.CHUNK_OVERLAP_CHARS)
        if not chunks:
            return SourceResult(url=url, verified=False, error="empty_page_content")

        async with self._llm_sem:
            selection = await asyncio.to_thread(
                self.llm.select_chunk, chunks, dim.claim_context, location
            )

        if not selection.get("relevant", False):
            return SourceResult(url=url, verified=False, error="not_relevant")

        idx = selection.get("chunk_index", -1)
        if idx < 0 or idx >= len(chunks):
            return SourceResult(url=url, verified=False, error="invalid_chunk_index")

        excerpt = chunks[idx].strip()
        data = selection.get("data", "").strip()

        if not verify_excerpt(excerpt, fetch_result.text):
            return SourceResult(
                url=url, verified=False, excerpt=excerpt, error="excerpt_not_found_in_source"
            )

        async with self._llm_sem:
            critique = await asyncio.to_thread(
                self.llm.critique_relevance, data, excerpt, dim.claim_context, location
            )

        return SourceResult(
            url=url,
            verified=True,
            data=data,
            excerpt=excerpt,
            low_relevance=not critique.get("relevant", True),
            critique_reason=critique.get("reason", ""),
        )
