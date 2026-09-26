"""Split page text into overlapping chunks. Chunks never cross page boundaries,
so every chunk maps to exactly one page number for citations."""
from dataclasses import dataclass

from app.ingest.pdf_reader import Page


@dataclass
class Chunk:
    text: str
    page: int
    index: int  # position within the document


def split_text(text: str, size: int, overlap: int) -> list[str]:
    if size <= 0 or overlap < 0 or overlap >= size:
        raise ValueError("require 0 <= overlap < size")
    words = text.split()
    chunks: list[str] = []
    start = 0
    while start < len(words):
        end, length = start, 0
        # always take at least one word, even if it alone exceeds size
        while end < len(words) and (end == start or length + len(words[end]) + 1 <= size):
            length += len(words[end]) + 1
            end += 1
        chunks.append(" ".join(words[start:end]))
        if end >= len(words):
            break
        back, olen = end, 0
        while back > start + 1 and olen + len(words[back - 1]) + 1 <= overlap:
            back -= 1
            olen += len(words[back]) + 1
        start = back
    return chunks


def chunk_pages(pages: list[Page], size: int, overlap: int) -> list[Chunk]:
    out: list[Chunk] = []
    for page in pages:
        for text in split_text(page.text, size, overlap):
            out.append(Chunk(text=text, page=page.number, index=len(out)))
    return out
