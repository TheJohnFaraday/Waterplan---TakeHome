"""Tiered fetch: static HTTP first, optional headless fallback (see ADR-005).

Static fetch is unconditional (no extra deps). Headless fallback (Playwright) is a
real, working code path but gated behind an optional import so the tool runs with
zero setup friction when Playwright isn't installed -- it degrades to
[FAILED VALIDATION: fetch blocked] instead of crashing.
"""

import asyncio
import logging
from collections import defaultdict

import httpx
from bs4 import BeautifulSoup

from waterplan.cache import FetchCache

logger = logging.getLogger(__name__)

try:
    from playwright.async_api import async_playwright

    HEADLESS_AVAILABLE = True
except ImportError:
    HEADLESS_AVAILABLE = False
    logger.info("[INFO] Playwright not installed; headless fallback unavailable.")

USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0 Safari/537.36 WaterplanRiskResearchBot/1.0"
)

MIN_STATIC_TEXT_LEN = 200  # below this, treat as a likely JS-shell page


class FetchResult:
    def __init__(self, url: str, ok: bool, text: str = "", error: str = ""):
        self.url = url
        self.ok = ok
        self.text = text
        self.error = error


def _domain(url: str) -> str:
    return httpx.URL(url).host or url


def _html_to_text(html: str) -> str:
    soup = BeautifulSoup(html, "lxml")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    return soup.get_text(separator=" ", strip=True)


class Fetcher:
    def __init__(self, cache: FetchCache, global_concurrency: int, per_domain_concurrency: int):
        self.cache = cache
        self._global_sem = asyncio.Semaphore(global_concurrency)
        self._domain_sems: dict[str, asyncio.Semaphore] = defaultdict(
            lambda: asyncio.Semaphore(per_domain_concurrency)
        )

    async def fetch(self, url: str) -> FetchResult:
        cached = self.cache.get(url)
        if cached is not None:
            return FetchResult(url, ok=True, text=cached)

        domain_sem = self._domain_sems[_domain(url)]
        async with self._global_sem, domain_sem:
            result = await self._fetch_static(url)
            if result.ok and len(result.text) >= MIN_STATIC_TEXT_LEN:
                self.cache.set(url, result.text)
                return result
            if HEADLESS_AVAILABLE:
                headless_result = await self._fetch_headless(url)
                if headless_result.ok:
                    self.cache.set(url, headless_result.text)
                    return headless_result
                return headless_result
            return FetchResult(
                url,
                ok=False,
                error="fetch_blocked_or_js_rendered_no_headless_fallback_available",
            )

    async def _fetch_static(self, url: str) -> FetchResult:
        try:
            async with httpx.AsyncClient(
                timeout=15, follow_redirects=True, headers={"User-Agent": USER_AGENT}
            ) as client:
                resp = await client.get(url)
                if resp.status_code >= 400:
                    return FetchResult(url, ok=False, error=f"http_{resp.status_code}")
                text = _html_to_text(resp.text)
                return FetchResult(url, ok=True, text=text)
        except httpx.HTTPError as e:
            return FetchResult(url, ok=False, error=f"fetch_error: {e}")

    async def _fetch_headless(self, url: str) -> FetchResult:
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch()
                page = await browser.new_page(user_agent=USER_AGENT)
                await page.goto(url, timeout=20000, wait_until="networkidle")
                html = await page.content()
                await browser.close()
                return FetchResult(url, ok=True, text=_html_to_text(html))
        except Exception as e:  # noqa: BLE001 - headless fetch has many possible failure modes
            return FetchResult(url, ok=False, error=f"headless_fetch_error: {e}")
