import io

from pypdf import PdfWriter

from tests.conftest import HANDBOOK


def test_upload_indexes_pdf(client, upload):
    r = upload(HANDBOOK)
    assert r.status_code == 201
    doc = r.json()["document"]
    assert doc["num_pages"] == 3
    assert doc["num_chunks"] >= 3
    assert r.json()["duplicate"] is False
    assert client.get("/health").json()["chunks"] == doc["num_chunks"]


def test_duplicate_upload_is_detected(client, upload):
    first = upload(HANDBOOK).json()
    second = upload(HANDBOOK, name="renamed.pdf")
    assert second.status_code == 201
    assert second.json()["duplicate"] is True
    assert second.json()["document"]["id"] == first["document"]["id"]
    assert len(client.get("/documents").json()) == 1


def test_non_pdf_extension_rejected(client):
    r = client.post("/documents", files={"file": ("notes.txt", b"hello", "text/plain")})
    assert r.status_code == 415


def test_fake_pdf_rejected(client):
    r = client.post("/documents", files={"file": ("fake.pdf", b"not really a pdf", "application/pdf")})
    assert r.status_code == 422


def test_pdf_without_text_rejected(client):
    buf = io.BytesIO()
    w = PdfWriter()
    w.add_blank_page(width=200, height=200)
    w.write(buf)
    r = client.post("/documents", files={"file": ("blank.pdf", buf.getvalue(), "application/pdf")})
    assert r.status_code == 422
    assert "scanned" in r.json()["detail"]


def test_list_download_and_delete(client, upload):
    doc_id = upload(HANDBOOK).json()["document"]["id"]
    assert [d["id"] for d in client.get("/documents").json()] == [doc_id]

    f = client.get(f"/documents/{doc_id}/file")
    assert f.status_code == 200 and f.content.startswith(b"%PDF")

    assert client.delete(f"/documents/{doc_id}").status_code == 204
    assert client.get("/documents").json() == []
    assert client.get("/health").json()["chunks"] == 0
    assert client.delete(f"/documents/{doc_id}").status_code == 404


def test_index_page_served(client):
    r = client.get("/")
    assert r.status_code == 200
    assert "Docs RAG Chatbot" in r.text
