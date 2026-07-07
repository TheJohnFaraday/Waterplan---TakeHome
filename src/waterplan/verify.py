"""Deterministic excerpt verification. No LLM in this file (see ADR-002)."""

import unicodedata


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFKC", text)
    text = " ".join(text.split())
    return text.lower()


def verify_excerpt(excerpt: str, page_text: str) -> bool:
    if not excerpt or not page_text:
        return False
    return normalize(excerpt) in normalize(page_text)


def chunk_text(text: str, chunk_size: int, overlap: int) -> list[str]:
    chunks = []
    start = 0
    n = len(text)
    while start < n:
        end = min(start + chunk_size, n)
        chunks.append(text[start:end])
        if end == n:
            break
        start = end - overlap
    return chunks
