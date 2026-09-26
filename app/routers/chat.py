from fastapi import APIRouter
from fastapi.concurrency import run_in_threadpool

from app.rag.answer import answer_question
from app.schemas import AskIn, AskOut

router = APIRouter(tags=["chat"])


@router.post("/ask", response_model=AskOut)
async def ask(body: AskIn) -> AskOut:
    """Answer a question from the uploaded PDFs, with [n] citations to document + page."""
    return await run_in_threadpool(answer_question, body.question.strip(), body.doc_ids)
