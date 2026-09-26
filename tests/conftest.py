"""Tests run fully offline: temp data dir, hash embedder (no model download),
canned LLM (no API key). Env is set before the app is imported and overrides any .env."""
import os
import tempfile
from pathlib import Path

_tmp = tempfile.mkdtemp(prefix="rag-tests-")
os.environ.update(
    DATA_DIR=_tmp,
    DATABASE_URL="",
    SEED_ON_STARTUP="false",
    GROQ_API_KEY="",
    EMBEDDING_BACKEND="hash",
)

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.db import Base, engine, init_db  # noqa: E402
from app.rag.vector_store import get_vector_store  # noqa: E402
from main import app  # noqa: E402

SAMPLES = Path(__file__).resolve().parent.parent / "sample_docs"
HANDBOOK = SAMPLES / "brightwater-employee-handbook.pdf"
API_REF = SAMPLES / "brightwater-api-reference.pdf"
SECURITY = SAMPLES / "brightwater-security-policy.pdf"


@pytest.fixture(autouse=True)
def _fresh_state():
    init_db()
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    get_vector_store().reset()
    yield


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture
def upload(client):
    def _upload(path: Path, name: str | None = None):
        with open(path, "rb") as f:
            return client.post("/documents", files={"file": (name or path.name, f, "application/pdf")})

    return _upload


@pytest.fixture
def seeded(upload):
    ids = {}
    for p in (HANDBOOK, API_REF, SECURITY):
        r = upload(p)
        assert r.status_code == 201, r.text
        ids[p.name] = r.json()["document"]["id"]
    return ids
