"""Static config: dimensions and default locations (see ADR-001..005)."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Dimension:
    key: str
    label: str
    emoji: str
    search_query_template: str
    claim_context: str
    ordinal: bool = False
    blocked_domains: tuple[str, ...] = ()


# Known interactive map/dashboard domains that return mostly JS app-shell text with
# no location-specific content in static HTML -- see ADR-003 "known limitation":
# this is a blocklist of specific domains observed to fail, not a general fix for
# unseen dashboard-style sources.
WATER_STRESS_BLOCKED_DOMAINS = (
    "wri.org/applications/aqueduct",
    "resourcewatch.org",
    "esri.com",
)

DIMENSIONS = [
    Dimension(
        key="water_stress",
        label="Water Stress",
        emoji="💧",
        search_query_template="{location} water stress level WRI aqueduct",
        claim_context=(
            "the level of water scarcity / physical water risk in this area. "
            "If the source gives a standardized score or category (e.g. WRI Aqueduct "
            "0-5 score, or Low/Medium-High/High/Extremely High), include it verbatim "
            "in your summary."
        ),
        ordinal=True,
        blocked_domains=WATER_STRESS_BLOCKED_DOMAINS,
    ),
    Dimension(
        key="incidents",
        label="Incidents",
        emoji="⚠️",
        search_query_template="{location} water protest strike conflict incident",
        claim_context=(
            "reports of strikes, protests, or previous water-related crises tied to "
            "this location."
        ),
    ),
    Dimension(
        key="regulations",
        label="Regulations",
        emoji="📜",
        search_query_template="{location} industrial water use regulation law",
        claim_context="relevant local regulations on industrial use of water.",
    ),
]

DEFAULT_LOCATIONS = [
    "Mexicali, Mexico",
    "Monterrey, Mexico",
    "Chandler, Arizona, USA",
]

MIN_VERIFIED_SOURCES = 2
MAX_CANDIDATE_URLS_PER_DIMENSION = 5
WEB_SEARCH_MAX_USES = 3

LLM_CONCURRENCY = 4
FETCH_CONCURRENCY_PER_DOMAIN = 2
FETCH_CONCURRENCY_GLOBAL = 10

CHUNK_SIZE_CHARS = 800
CHUNK_OVERLAP_CHARS = 100

CACHE_DIR = ".cache"
OUTPUT_DIR = "output"
