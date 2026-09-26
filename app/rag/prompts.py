from app.rag.vector_store import Hit

SYSTEM_PROMPT = """You answer questions using ONLY the numbered sources provided.
Rules:
- Cite every claim with the source number in square brackets, e.g. [1] or [2][3].
- If the sources do not contain the answer, reply exactly: "I couldn't find that in the uploaded documents."
- Do not use outside knowledge. Do not invent source numbers.
- Be concise: at most 5 sentences unless the user asks for more detail."""


def format_sources(hits: list[Hit]) -> str:
    return "\n\n".join(f"[{i}] ({h.filename}, page {h.page})\n{h.text}" for i, h in enumerate(hits, start=1))


def build_user_prompt(question: str, hits: list[Hit]) -> str:
    return f"Sources:\n\n{format_sources(hits)}\n\nQuestion: {question}"
