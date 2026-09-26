"""Groq free tier through the OpenAI-compatible API."""
import openai

from app.config import Settings
from app.llm.base import LLMError
from app.rag.prompts import SYSTEM_PROMPT, build_user_prompt
from app.rag.vector_store import Hit


class GroqClient:
    name = "groq"

    def __init__(self, settings: Settings):
        self.model = settings.groq_model
        self.temperature = settings.llm_temperature
        self.client = openai.OpenAI(
            api_key=settings.groq_api_key,
            base_url=settings.groq_base_url,
            timeout=settings.llm_timeout_seconds,
            max_retries=2,
        )

    def answer(self, question: str, sources: list[Hit]) -> str:
        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                temperature=self.temperature,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": build_user_prompt(question, sources)},
                ],
            )
        except openai.OpenAIError as exc:
            raise LLMError(str(exc)) from exc
        content = resp.choices[0].message.content if resp.choices else None
        if not content:
            raise LLMError("Empty response from model")
        return content.strip()
