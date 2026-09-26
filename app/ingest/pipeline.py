"""Upload pipeline: validate → dedupe by hash → read → chunk → embed → store."""
import hashlib
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.ingest.chunker import chunk_pages
from app.ingest.pdf_reader import read_pdf
from app.models import Document
from app.rag.embeddings import get_embedder
from app.rag.vector_store import get_vector_store


@dataclass
class IngestResult:
    document: Document
    duplicate: bool


def ingest_pdf(db: Session, filename: str, data: bytes) -> IngestResult:
    """Raises PdfError for unreadable files. Re-uploading identical bytes is a no-op."""
    s = get_settings()
    digest = hashlib.sha256(data).hexdigest()
    existing = db.scalar(select(Document).where(Document.sha256 == digest))
    if existing:
        return IngestResult(existing, duplicate=True)

    pages = read_pdf(data)
    chunks = chunk_pages(pages, s.chunk_size, s.chunk_overlap)
    embeddings = get_embedder().embed([c.text for c in chunks])

    doc = Document(
        filename=filename,
        sha256=digest,
        num_pages=len(pages),
        num_chunks=len(chunks),
        size_bytes=len(data),
    )
    db.add(doc)
    db.flush()  # assigns doc.id

    store = get_vector_store()
    store.add(doc.id, filename, chunks, embeddings)
    try:
        s.upload_dir.mkdir(parents=True, exist_ok=True)
        (s.upload_dir / f"{doc.id}.pdf").write_bytes(data)
        db.commit()
    except Exception:
        db.rollback()
        store.delete(doc.id)
        raise
    return IngestResult(doc, duplicate=False)


def delete_document(db: Session, doc: Document) -> None:
    get_vector_store().delete(doc.id)
    (get_settings().upload_dir / f"{doc.id}.pdf").unlink(missing_ok=True)
    db.delete(doc)
    db.commit()
