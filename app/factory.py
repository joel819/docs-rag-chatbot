import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse

from app.config import get_settings
from app.db import init_db
from app.routers import chat, documents, health

log = logging.getLogger("uvicorn.error")
STATIC = Path(__file__).parent / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):
    s = get_settings()
    init_db()
    if s.seed_on_startup:
        from scripts.seed import seed

        seed(verbose=False)
    if s.demo_mode:
        log.warning("DEMO MODE: no GROQ_API_KEY set. Answers are extractive quotes from your PDFs.")
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title=get_settings().app_name,
        version="0.1.0",
        description="Upload PDFs and ask questions. Answers cite document and page.",
        lifespan=lifespan,
    )
    for r in (health.router, documents.router, chat.router):
        app.include_router(r)

    @app.get("/", include_in_schema=False)
    def index():
        return FileResponse(STATIC / "index.html")

    return app
