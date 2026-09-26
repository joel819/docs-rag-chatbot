from typing import Protocol

from app.rag.vector_store import Hit


class LLMError(Exception):
    """The LLM call failed (network, rate limit, bad response). Caller falls back."""


class LLMClient(Protocol):
    name: str

    def answer(self, question: str, sources: list[Hit]) -> str:
        """Return an answer that cites sources as [n], 1-based into `sources`."""
        ...
