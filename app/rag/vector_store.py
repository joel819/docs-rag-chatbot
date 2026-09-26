"""ChromaDB persistent store. We pass our own embeddings, so Chroma never
downloads its default embedding model."""
from dataclasses import dataclass
from functools import lru_cache

import chromadb
from chromadb.config import Settings as ChromaSettings

from app.config import get_settings
from app.ingest.chunker import Chunk

COLLECTION = "doc_chunks"


@dataclass
class Hit:
    text: str
    doc_id: str
    filename: str
    page: int
    score: float  # cosine similarity, higher is better


class VectorStore:
    def __init__(self, path: str):
        self.client = chromadb.PersistentClient(path=path, settings=ChromaSettings(anonymized_telemetry=False))
        self.collection = self._collection()

    def _collection(self):
        return self.client.get_or_create_collection(
            COLLECTION, embedding_function=None, metadata={"hnsw:space": "cosine"}
        )

    def add(self, doc_id: str, filename: str, chunks: list[Chunk], embeddings: list[list[float]]) -> None:
        if not chunks:
            return
        self.collection.add(
            ids=[f"{doc_id}:{c.index}" for c in chunks],
            embeddings=embeddings,
            documents=[c.text for c in chunks],
            metadatas=[{"doc_id": doc_id, "filename": filename, "page": c.page, "chunk": c.index} for c in chunks],
        )

    def query(self, embedding: list[float], k: int, doc_ids: list[str] | None = None) -> list[Hit]:
        total = self.collection.count()
        if total == 0:
            return []
        where = {"doc_id": {"$in": doc_ids}} if doc_ids else None
        res = self.collection.query(
            query_embeddings=[embedding],
            n_results=min(k, total),
            where=where,
            include=["documents", "metadatas", "distances"],
        )
        return [
            Hit(text=d, doc_id=m["doc_id"], filename=m["filename"], page=int(m["page"]), score=1.0 - dist)
            for d, m, dist in zip(res["documents"][0], res["metadatas"][0], res["distances"][0], strict=True)
        ]

    def delete(self, doc_id: str) -> None:
        self.collection.delete(where={"doc_id": doc_id})

    def count(self) -> int:
        return self.collection.count()

    def reset(self) -> None:
        self.client.delete_collection(COLLECTION)
        self.collection = self._collection()


@lru_cache
def get_vector_store() -> VectorStore:
    path = get_settings().chroma_dir
    path.mkdir(parents=True, exist_ok=True)
    return VectorStore(str(path))
