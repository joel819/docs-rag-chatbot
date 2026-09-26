from app.rag.retriever import retrieve


def test_finds_right_document_and_page(seeded):
    hits = retrieve("How many days of paid time off per calendar year?")
    assert hits
    assert hits[0].filename == "brightwater-employee-handbook.pdf"
    assert hits[0].page == 2


def test_finds_rate_limit_page(seeded):
    top = retrieve("API rate limits requests per minute 429")[0]
    assert top.filename == "brightwater-api-reference.pdf"
    assert top.page == 2


def test_doc_filter_restricts_results(seeded):
    only = seeded["brightwater-security-policy.pdf"]
    hits = retrieve("paid time off days", doc_ids=[only])
    assert all(h.doc_id == only for h in hits)


def test_empty_store_returns_nothing():
    assert retrieve("anything") == []
