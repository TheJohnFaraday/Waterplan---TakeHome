"""Disk cache keyed by URL, storing raw fetched page text (bonus scope).

Avoids duplicate fetches across re-runs. Not a correctness dependency: verification
(ADR-002) always re-checks the excerpt against whatever text is in the cache entry used,
so a stale cache entry can only produce a false [FAILED VALIDATION] (safe direction),
never a false MATCH.
"""

import hashlib
import json
import time
from pathlib import Path


class FetchCache:
    def __init__(self, cache_dir: str, ttl_seconds: int = 7 * 24 * 3600):
        self.dir = Path(cache_dir)
        self.dir.mkdir(parents=True, exist_ok=True)
        self.ttl_seconds = ttl_seconds

    def _path_for(self, url: str) -> Path:
        key = hashlib.sha256(url.encode("utf-8")).hexdigest()
        return self.dir / f"{key}.json"

    def get(self, url: str) -> str | None:
        path = self._path_for(url)
        if not path.exists():
            return None
        try:
            record = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return None
        if time.time() - record.get("fetched_at", 0) > self.ttl_seconds:
            return None
        return record.get("text")

    def set(self, url: str, text: str) -> None:
        path = self._path_for(url)
        record = {"url": url, "text": text, "fetched_at": time.time()}
        path.write_text(json.dumps(record), encoding="utf-8")
