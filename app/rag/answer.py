"""Retrieve → generate → map [n] markers back to document + page."""
import re

from app.llm import get_llm
from app.llm.base import LLMError
from app.llm.canned_client import NOT_FOUND, CannedClient
from app.rag.retriever import retrieve
from app.rag.vector_store import Hit
from app.schemas import AskOut, Citation

_MARKER = re.compile(r"\[(\d+)\]")
# Some models write citations as 【1】 or ［1］; normalise them to [1].
_ALT_MARKER = re.compile(r"[【［\[]\s*(\d+)\s*[】］\]]")


def _citations(answer: str, hits: list[Hit]) -> tuple[str, list[Citation]]:
    answer = _ALT_MARKER.sub(lambda m: f"[{m.group(1)}]", answer)
    used: list[int] = []
    for m in _MARKER.finditer(answer):
        n = int(m.group(1))
        if 1 <= n <= len(hits) and n not in used:
            used.append(n)
    # Drop markers pointing at sources that don't exist (hallucinated numbers).
    answer = _MARKER.sub(lambda m: m.group(0) if 1 <= int(m.group(1)) <= len(hits) else "", answer).strip()
    cites = [
        Citation(
            n=n,
            doc_id=hits[n - 1].doc_id,
            filename=hits[n - 1].filename,
            page=hits[n - 1].page,
            snippet=hits[n - 1].text[:280],
            score=round(hits[n - 1].score, 4),
        )
        for n in used
    ]
    return answer, cites


def answer_question(question: str, doc_ids: list[str] | None = None) -> AskOut:
    llm = get_llm()
    mode = "demo" if llm.name == "canned" else "groq"
    hits = retrieve(question, doc_ids)
    if not hits:
        return AskOut(answer=NOT_FOUND, citations=[], mode=mode)
    try:
        text = llm.answer(question, hits)
    except LLMError:
        text, mode = CannedClient().answer(question, hits), "fallback"
    text, cites = _citations(text, hits)
    return AskOut(answer=text or NOT_FOUND, citations=cites, mode=mode)
