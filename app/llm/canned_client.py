"""Demo-mode answerer: no API key needed.

Extractive, not generative: it picks the sentences from the retrieved chunks that
best overlap the question and cites where each came from. Everything it says is
quoted from your documents, so it never makes things up.
"""
import math
import re

from app.rag.text import terms as _terms
from app.rag.vector_store import Hit

NOT_FOUND = "I couldn't find that in the uploaded documents."

_SENT = re.compile(r"(?<=[.!?])\s+")


class CannedClient:
    name = "canned"
    max_sentences = 3
    # keep only sentences at least this fraction as relevant as the best one
    relative_cutoff = 0.6

    def answer(self, question: str, sources: list[Hit]) -> str:
        q = _terms(question)
        scored: list[tuple[int, float, int, int, str]] = []
        for n, hit in enumerate(sources, start=1):
            heading: set[str] = set()
            for pos, sent in enumerate(_SENT.split(hit.text.replace("\n", " "))):
                sent = sent.strip()
                if len(sent) < 30:
                    # short "sentences" are section headings: their words give context
                    # to the sentences below them, but aren't quoted themselves
                    heading = _terms(sent)
                    continue
                overlap = len(q & (_terms(sent) | heading))
                if overlap:
                    scored.append((overlap, hit.score, n, pos, sent))
        if not scored:
            # Nothing in the retrieved text shares a keyword with the question: say so
            # rather than quoting something irrelevant.
            return NOT_FOUND
        # term overlap first, retrieval score as tie-breaker
        scored.sort(key=lambda t: (-t[0], -t[1]))
        floor = max(1, math.ceil(scored[0][0] * self.relative_cutoff))
        best = [t for t in scored if t[0] >= floor][: self.max_sentences]
        best.sort(key=lambda t: (t[2], t[3]))  # read in document order
        parts = [f"{s.rstrip('.')}. [{n}]" for _, _, n, _, s in best]
        return "From your documents: " + " ".join(parts)
