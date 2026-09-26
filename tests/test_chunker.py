import pytest

from app.ingest.chunker import chunk_pages, split_text
from app.ingest.pdf_reader import Page


def test_short_text_is_one_chunk():
    assert split_text("hello world", 100, 10) == ["hello world"]


def test_chunks_respect_size():
    text = " ".join(f"word{i}" for i in range(500))
    for c in split_text(text, 200, 40):
        assert len(c) <= 200


def test_chunks_overlap():
    text = " ".join(f"w{i}" for i in range(200))
    chunks = split_text(text, 100, 30)
    assert len(chunks) > 1
    for a, b in zip(chunks, chunks[1:]):
        assert a.split()[-1] in b.split()  # tail of one chunk reappears in the next


def test_all_words_covered_in_order():
    words = [f"w{i}" for i in range(300)]
    chunks = split_text(" ".join(words), 120, 30)
    seen = []
    for c in chunks:
        for w in c.split():
            if not seen or int(w[1:]) > int(seen[-1][1:]):
                seen.append(w)
    assert seen == words


def test_oversized_single_word_still_progresses():
    chunks = split_text("x" * 50 + " tail", 10, 2)
    assert chunks == ["x" * 50, "tail"]


def test_invalid_overlap_rejected():
    with pytest.raises(ValueError):
        split_text("a b c", 10, 10)


def test_chunks_never_cross_pages_and_keep_page_numbers():
    pages = [Page(1, "alpha " * 100), Page(2, ""), Page(3, "gamma " * 10)]
    chunks = chunk_pages(pages, 120, 20)
    assert {c.page for c in chunks} == {1, 3}
    assert all("gamma" not in c.text for c in chunks if c.page == 1)
    assert [c.index for c in chunks] == list(range(len(chunks)))
