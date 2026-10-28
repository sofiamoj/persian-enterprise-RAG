import io

import pytest

from rag.ingest import ingest
from rag.models import Chunk
from rag.retrieval import retrieve

pytestmark = pytest.mark.django_db


def _add(name, text):
    return ingest(name, io.BytesIO(text.encode("utf-8")))


def test_ingest_stores_chunks_with_embeddings():
    doc = _add("a.txt", "photosynthesis turns light into chemical energy")
    chunk = Chunk.objects.get(document=doc)
    assert chunk.index == 0 and len(chunk.embedding) == 384


def test_most_similar_chunk_comes_first_with_citation():
    _add("plants.txt", "photosynthesis turns sunlight water and carbon dioxide into glucose")
    _add("fable.txt", "the tortoise won the race against the sleeping hare")
    _add("hafez.txt", "حافظ شاعر بزرگ شیراز و دیوان غزلیات او")

    top = retrieve("how does photosynthesis use sunlight?", k=2)
    assert top[0]["document"] == "plants.txt" and top[0]["chunk"] == 1
    assert top[0]["score"] > top[1]["score"]

    assert retrieve("شاعر شیراز حافظ", k=1)[0]["document"] == "hafez.txt"


def test_unsupported_and_empty_files_are_rejected():
    with pytest.raises(ValueError):
        ingest("x.exe", io.BytesIO(b"data"))
    with pytest.raises(ValueError):
        _add("empty.txt", "   ")
