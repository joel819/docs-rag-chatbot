from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.db import get_db
from app.ingest.pdf_reader import PdfError
from app.ingest.pipeline import delete_document, ingest_pdf
from app.models import Document
from app.schemas import DocumentOut, UploadOut

router = APIRouter(prefix="/documents", tags=["documents"])


def _get_or_404(db: Session, doc_id: str) -> Document:
    doc = db.get(Document, doc_id)
    if doc is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Document not found")
    return doc


@router.post("", response_model=UploadOut, status_code=status.HTTP_201_CREATED)
async def upload(file: UploadFile = File(...), db: Session = Depends(get_db)):
    limit = get_settings().max_upload_mb * 1024 * 1024
    data = await file.read(limit + 1)
    if len(data) > limit:
        raise HTTPException(status.HTTP_413_CONTENT_TOO_LARGE, f"Max upload size is {limit // 1048576} MB")
    name = (file.filename or "upload.pdf").rsplit("/", 1)[-1].rsplit("\\", 1)[-1][:255]
    if not name.lower().endswith(".pdf"):
        raise HTTPException(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, "Only PDF files are supported")
    try:
        # embedding is CPU-bound; keep the event loop free
        result = await run_in_threadpool(ingest_pdf, db, name, data)
    except PdfError as exc:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, str(exc)) from None
    return UploadOut(document=DocumentOut.model_validate(result.document), duplicate=result.duplicate)


@router.get("", response_model=list[DocumentOut])
def list_documents(db: Session = Depends(get_db)):
    return db.scalars(select(Document).order_by(Document.created_at.desc())).all()


@router.get("/{doc_id}/file")
def download(doc_id: str, db: Session = Depends(get_db)):
    doc = _get_or_404(db, doc_id)
    path = get_settings().upload_dir / f"{doc.id}.pdf"
    if not path.exists():
        raise HTTPException(status.HTTP_404_NOT_FOUND, "File missing")
    return FileResponse(path, media_type="application/pdf", filename=doc.filename,
                        content_disposition_type="inline")


@router.delete("/{doc_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove(doc_id: str, db: Session = Depends(get_db)):
    delete_document(db, _get_or_404(db, doc_id))
