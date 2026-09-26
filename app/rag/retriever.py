from app.config import get_settings
from app.rag.embeddings import get_embedder
from app.rag.vector_store import Hit, get_vector_store


def retrieve(question: str, doc_ids: list[str] | None = None) -> list[Hit]:
    s = get_settings()
    [vec] = get_embedder().embed([question])
    hits = get_vector_store().query(vec, s.top_k, doc_ids)
    return [h for h in hits if h.score >= s.effective_min_score]
