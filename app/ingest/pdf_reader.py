"""Extract text per page from a PDF, keeping 1-based page numbers."""
import re
from dataclasses import dataclass
from io import BytesIO

from pypdf import PdfReader
from pypdf.errors import PdfReadError


class PdfError(Exception):
    """File is not a readable PDF, is encrypted, or has no extractable text."""


@dataclass
class Page:
    number: int  # 1-based
    text: str


_WS = re.compile(r"[ \t]+")


_HEADING_MAX = 60


def _clean(text: str) -> str:
    text = text.replace("\x00", "")
    text = re.sub(r"-\n(\w)", r"\1", text)  # re-join hyphenated line breaks
    lines = [ln for ln in (_WS.sub(" ", ln).strip() for ln in text.splitlines()) if ln]
    # Short unpunctuated lines are almost always headings. End them with a period so
    # they don't run into the next sentence once chunks are joined with spaces.
    for i, ln in enumerate(lines[:-1]):
        if len(ln) <= _HEADING_MAX and ln[-1] not in ".!?:;,":
            lines[i] = ln + "."
    return "\n".join(lines)


def read_pdf(data: bytes) -> list[Page]:
    if not data.startswith(b"%PDF"):
        raise PdfError("File is not a PDF")
    try:
        reader = PdfReader(BytesIO(data))
        if reader.is_encrypted:
            raise PdfError("Encrypted PDFs are not supported")
        pages = [Page(i, _clean(p.extract_text() or "")) for i, p in enumerate(reader.pages, start=1)]
    except PdfReadError as exc:
        raise PdfError(f"Could not read PDF: {exc}") from None
    if not any(p.text for p in pages):
        raise PdfError("No extractable text found (is it a scanned PDF?)")
    return pages
