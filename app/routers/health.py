from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.db import get_db
from app.models import Document
from app.rag.vector_store import get_vector_store

router = APIRouter(tags=["health"])


@router.get("/health")
def health(db: Session = Depends(get_db)) -> dict:
    s = get_settings()
    return {
        "status": "ok",
        "demo_mode": s.demo_mode,
        "llm": "canned" if s.demo_mode else s.groq_model,
        "embeddings": "hash" if s.embedding_backend == "hash" else s.embedding_model,
        "documents": db.scalar(select(func.count()).select_from(Document)),
        "chunks": get_vector_store().count(),
    }
