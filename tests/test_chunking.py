import pytest

from rag.chunking import chunk_text


def test_empty_text_gives_no_chunks():
    assert chunk_text("   \n ") == []


def test_short_text_is_one_chunk():
    assert chunk_text("hello world", size=100, overlap=10) == ["hello world"]


def test_chunks_respect_size_and_overlap():
    text = " ".join(f"word{i}" for i in range(200))
    chunks = chunk_text(text, size=100, overlap=20)
    assert len(chunks) > 1
    assert all(len(c) <= 100 for c in chunks)
    # consecutive chunks share some text, and nothing is lost
    assert chunks[0].split()[-1] in chunks[1]
    assert chunks[0].startswith("word0") and chunks[-1].endswith("word199")


def test_persian_text_is_chunked():
    text = "این یک جمله فارسی است. " * 100
    chunks = chunk_text(text, size=120, overlap=30)
    assert len(chunks) > 1 and all("فارسی" in c for c in chunks)


def test_invalid_arguments():
    with pytest.raises(ValueError):
        chunk_text("abc", size=10, overlap=10)
    with pytest.raises(ValueError):
        chunk_text("abc", size=0)
