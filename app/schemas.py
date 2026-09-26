from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class DocumentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    filename: str
    num_pages: int
    num_chunks: int
    size_bytes: int
    created_at: datetime


class UploadOut(BaseModel):
    document: DocumentOut
    duplicate: bool = False


class AskIn(BaseModel):
    question: str = Field(min_length=1, max_length=1000)
    doc_ids: list[str] | None = Field(default=None, description="Limit search to these documents")


class Citation(BaseModel):
    n: int  # the [n] marker used in the answer
    doc_id: str
    filename: str
    page: int
    snippet: str
    score: float


class AskOut(BaseModel):
    answer: str
    citations: list[Citation]
    # groq = real LLM, demo = no key (extractive), fallback = Groq call failed (extractive)
    mode: Literal["groq", "demo", "fallback"]
