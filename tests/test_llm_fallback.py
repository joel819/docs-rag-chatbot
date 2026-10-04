from types import SimpleNamespace

import openai
import pytest

from app.config import get_settings
from app.llm import get_llm
from app.llm.base import LLMError
from app.llm.canned_client import CannedClient
from app.llm.groq_client import GroqClient
from app.rag import answer as answer_mod
from app.rag.vector_store import Hit

HITS = [
    Hit("Full-time employees receive 25 days of paid time off per calendar year.", "d1", "handbook.pdf", 2, 0.8),
    Hit("Sick leave is up to 10 days per year.", "d1", "handbook.pdf", 2, 0.5),
]


def _fake_completion(content):
    return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=content))])


@pytest.fixture
def groq():
    settings = get_settings().model_copy(update={"groq_api_key": "gsk_test_dummy"})
    return GroqClient(settings)


def test_no_key_uses_canned_client():
    assert isinstance(get_llm(), CannedClient)


def test_canned_client_quotes_and_cites():
    out = CannedClient().answer("How many paid time off days?", HITS)
    assert "25 days" in out and "[1]" in out


def test_groq_client_sends_sources_and_uses_right_model(groq, monkeypatch):
    captured = {}

    def fake_create(**kwargs):
        captured.update(kwargs)
        return _fake_completion("Employees get 25 days [1].")

    monkeypatch.setattr(groq.client.chat.completions, "create", fake_create)
    assert groq.answer("PTO?", HITS) == "Employees get 25 days [1]."
    assert captured["model"] == "openai/gpt-oss-120b"
    user_msg = captured["messages"][1]["content"]
    assert "[1] (handbook.pdf, page 2)" in user_msg
    assert str(groq.client.base_url).startswith("https://api.groq.com/openai/v1")


def test_groq_errors_become_llm_error(groq, monkeypatch):
    def boom(**kwargs):
        raise openai.APIConnectionError(request=None)

    monkeypatch.setattr(groq.client.chat.completions, "create", boom)
    with pytest.raises(LLMError):
        groq.answer("PTO?", HITS)


def test_empty_groq_response_is_error(groq, monkeypatch):
    monkeypatch.setattr(groq.client.chat.completions, "create", lambda **k: _fake_completion(""))
    with pytest.raises(LLMError):
        groq.answer("PTO?", HITS)


def test_failed_llm_call_falls_back_to_extractive(client, seeded, monkeypatch):
    class Failing:
        name = "groq"

        def answer(self, q, s):
            raise LLMError("rate limited")

    monkeypatch.setattr(answer_mod, "get_llm", lambda: Failing())
    body = client.post("/ask", json={"question": "How many days of paid time off?"}).json()
    assert body["mode"] == "fallback"
    assert "25 days" in body["answer"] and body["citations"]


def test_hallucinated_citation_numbers_are_dropped(client, seeded, monkeypatch):
    class Liar:
        name = "groq"

        def answer(self, q, s):
            return "Employees get 25 days [1][9]."

    monkeypatch.setattr(answer_mod, "get_llm", lambda: Liar())
    body = client.post("/ask", json={"question": "How many days of paid time off?"}).json()
    assert body["mode"] == "groq"
    assert "[9]" not in body["answer"]
    assert [c["n"] for c in body["citations"]] == [1]


def test_fullwidth_citation_markers_are_normalised():
    text, cites = answer_mod._citations("Employees get 25 days【1】 and 10 sick days［2］.", HITS)
    assert text == "Employees get 25 days[1] and 10 sick days[2]."
    assert [c.n for c in cites] == [1, 2]
