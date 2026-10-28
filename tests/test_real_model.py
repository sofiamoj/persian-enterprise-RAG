"""Optional smoke test with the real multilingual-e5-small model (downloads ~470 MB).
Run with: RUN_MODEL_TESTS=1 pytest tests/test_real_model.py"""
import io
import os

import pytest

from rag import embeddings
from rag.ingest import ingest
from rag.retrieval import retrieve

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.skipif(not os.environ.get("RUN_MODEL_TESTS"), reason="set RUN_MODEL_TESTS=1 to run"),
]


@pytest.fixture(autouse=True)
def fake_embeddings():  # override conftest: use the real model here
    yield


def test_cross_lingual_retrieval():
    ingest("hafez.txt", io.BytesIO("حافظ شاعر بزرگ ایرانی اهل شیراز بود و دیوان غزلیات دارد.".encode()))
    ingest("plants.txt", io.BytesIO(b"Photosynthesis converts light energy into chemical energy in plants."))
    assert retrieve("Who was the poet from Shiraz?", k=1)[0]["document"] == "hafez.txt"
    assert retrieve("how do plants use light?", k=1)[0]["document"] == "plants.txt"
