"""Index the sample PDFs in sample_docs/ so the demo works right after clone.
Safe to run repeatedly: already-indexed files are skipped by content hash.

Usage: python -m scripts.seed
"""
from pathlib import Path

from app.db import SessionLocal, init_db
from app.ingest.pipeline import ingest_pdf

SAMPLE_DIR = Path(__file__).resolve().parent.parent / "sample_docs"


def seed(verbose: bool = True) -> int:
    init_db()
    added = 0
    with SessionLocal() as db:
        for pdf in sorted(SAMPLE_DIR.glob("*.pdf")):
            result = ingest_pdf(db, pdf.name, pdf.read_bytes())
            added += not result.duplicate
            if verbose:
                state = "already indexed" if result.duplicate else f"{result.document.num_chunks} chunks"
                print(f"  {pdf.name:<36} {state}")
    if verbose:
        print(f"Seeded {added} new document(s).")
    return added


if __name__ == "__main__":
    seed()
