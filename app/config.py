"""Settings from environment variables / .env."""
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "docs-rag-chatbot"
    data_dir: Path = Path("./data")
    database_url: str = ""  # defaults to sqlite in data_dir
    seed_on_startup: bool = True
    max_upload_mb: int = 20

    # LLM (Groq free tier via the OpenAI-compatible API)
    groq_api_key: str = ""
    groq_base_url: str = "https://api.groq.com/openai/v1"
    groq_model: str = "openai/gpt-oss-120b"
    llm_timeout_seconds: float = 30.0
    llm_temperature: float = 0.1

    # Embeddings: "sentence-transformers" (real, local) or "hash" (offline, no model download)
    embedding_backend: str = "sentence-transformers"
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"

    # Chunking & retrieval
    chunk_size: int = 800  # characters
    chunk_overlap: int = 150
    top_k: int = 5
    # cosine similarity floor; unset = 0.2 for MiniLM, 0.05 for the hash embedder
    min_score: float | None = None

    @property
    def demo_mode(self) -> bool:
        return not self.groq_api_key

    @property
    def effective_min_score(self) -> float:
        if self.min_score is not None:
            return self.min_score
        return 0.05 if self.embedding_backend == "hash" else 0.2

    @property
    def sqlite_url(self) -> str:
        return self.database_url or f"sqlite:///{(self.data_dir / 'app.db').as_posix()}"

    @property
    def chroma_dir(self) -> Path:
        return self.data_dir / "chroma"

    @property
    def upload_dir(self) -> Path:
        return self.data_dir / "uploads"


@lru_cache
def get_settings() -> Settings:
    return Settings()
