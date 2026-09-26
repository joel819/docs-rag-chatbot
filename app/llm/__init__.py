from functools import lru_cache

from app.config import get_settings
from app.llm.base import LLMClient, LLMError


@lru_cache
def get_llm() -> LLMClient:
    """Groq when GROQ_API_KEY is set; otherwise the canned (extractive) demo client."""
    s = get_settings()
    if s.demo_mode:
        from app.llm.canned_client import CannedClient

        return CannedClient()
    from app.llm.groq_client import GroqClient

    return GroqClient(s)


__all__ = ["LLMClient", "LLMError", "get_llm"]
