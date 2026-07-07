"""Thin LLM interface (see ADR-005). Anthropic is the concrete implementation;
swapping providers means implementing LLMClient, not a rewrite of the pipeline.
"""

from abc import ABC, abstractmethod

from anthropic import Anthropic

SELECT_CHUNK_TOOL = {
    "name": "select_chunk",
    "description": (
        "Select which chunk (by index) best supports a claim about the given "
        "dimension, and state the claim briefly."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "chunk_index": {
                "type": "integer",
                "description": "Index of the chunk that best supports the claim.",
            },
            "data": {
                "type": "string",
                "description": "Short (<25 words) summary of what the chunk shows.",
            },
            "relevant": {
                "type": "boolean",
                "description": "False if no chunk actually supports this dimension for this location.",
            },
        },
        "required": ["chunk_index", "data", "relevant"],
    },
}


class LLMClient(ABC):
    @abstractmethod
    def select_chunk(self, chunks: list[str], claim_context: str, location: str) -> dict:
        """Returns {"chunk_index": int, "data": str, "relevant": bool}."""

    @abstractmethod
    def discover_urls(
        self, query: str, max_uses: int = 3, blocked_domains: tuple[str, ...] = ()
    ) -> list[dict]:
        """Returns a list of {"url": str, "title": str} candidates."""


class AnthropicLLMClient(LLMClient):
    def __init__(self, api_key: str | None = None, model: str = "claude-sonnet-5"):
        self.client = Anthropic(api_key=api_key)
        self.model = model

    def select_chunk(self, chunks: list[str], claim_context: str, location: str) -> dict:
        numbered = "\n\n".join(f"[{i}] {c}" for i, c in enumerate(chunks))
        prompt = (
            f"Location: {location}\n"
            f"Dimension to research: {claim_context}\n\n"
            f"Below are numbered text chunks fetched from a web page. Call select_chunk "
            f"with the index of the single chunk that best supports a claim about this "
            f"dimension for this location. Do not invent information not present in the "
            f"chunks. If none of the chunks are relevant, set relevant=false.\n\n{numbered}"
        )
        resp = self.client.messages.create(
            model=self.model,
            max_tokens=300,
            tools=[SELECT_CHUNK_TOOL],
            tool_choice={"type": "tool", "name": "select_chunk"},
            messages=[{"role": "user", "content": prompt}],
        )
        for block in resp.content:
            if block.type == "tool_use" and block.name == "select_chunk":
                return block.input
        return {"chunk_index": -1, "data": "", "relevant": False}

    def discover_urls(
        self, query: str, max_uses: int = 3, blocked_domains: tuple[str, ...] = ()
    ) -> list[dict]:
        web_search_tool = {"type": "web_search_20250305", "name": "web_search", "max_uses": max_uses}
        if blocked_domains:
            web_search_tool["blocked_domains"] = list(blocked_domains)
        resp = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            tools=[web_search_tool],
            messages=[{"role": "user", "content": f"Search for: {query}"}],
        )
        results = []
        seen_urls = set()
        for block in resp.content:
            if block.type == "web_search_tool_result":
                content = block.content
                if isinstance(content, list):
                    for item in content:
                        url = getattr(item, "url", None)
                        title = getattr(item, "title", "")
                        if url and url not in seen_urls:
                            seen_urls.add(url)
                            results.append({"url": url, "title": title})
        return results
