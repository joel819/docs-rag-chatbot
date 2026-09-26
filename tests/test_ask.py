import re


def test_answer_cites_document_and_page(client, seeded):
    r = client.post("/ask", json={"question": "How many days of paid time off do full-time employees get?"})
    assert r.status_code == 200
    body = r.json()
    assert body["mode"] == "demo"
    assert "25 days" in body["answer"]
    assert body["citations"]
    top = body["citations"][0]
    assert top["filename"] == "brightwater-employee-handbook.pdf"
    assert top["page"] == 2
    # every [n] in the answer has a matching citation
    markers = {int(n) for n in re.findall(r"\[(\d+)\]", body["answer"])}
    assert markers == {c["n"] for c in body["citations"]}


def test_incident_reporting_question(client, seeded):
    body = client.post("/ask", json={"question": "How quickly must a security incident be reported?"}).json()
    assert "1 hour" in body["answer"]
    assert any(c["filename"] == "brightwater-security-policy.pdf" and c["page"] == 3 for c in body["citations"])


def test_no_documents_says_not_found(client):
    body = client.post("/ask", json={"question": "What is the refund policy?"}).json()
    assert body["citations"] == []
    assert "couldn't find" in body["answer"]


def test_empty_question_rejected(client):
    assert client.post("/ask", json={"question": ""}).status_code == 422


def test_doc_filter_via_api(client, seeded):
    api_id = seeded["brightwater-api-reference.pdf"]
    body = client.post("/ask", json={"question": "rate limit requests per minute", "doc_ids": [api_id]}).json()
    assert body["citations"]
    assert all(c["doc_id"] == api_id for c in body["citations"])


def test_out_of_scope_question_is_not_answered(client, seeded):
    body = client.post("/ask", json={"question": "What is the capital of France?"}).json()
    assert "couldn't find" in body["answer"]
    assert body["citations"] == []


def test_heading_context_helps_pick_the_right_sentence(client, seeded):
    body = client.post("/ask", json={"question": "What is the API rate limit?"}).json()
    assert "120 requests per minute" in body["answer"]
