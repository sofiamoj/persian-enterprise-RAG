import hashlib
import re

import pytest
from django.conf import settings

from rag import embeddings


def _fake_vector(text: str) -> list[float]:
    """Deterministic bag-of-words hashing embedding: shared words => higher cosine similarity."""
    vec = [0.0] * settings.EMBEDDING_DIM
    for word in re.findall(r"\w+", text.lower().replace("passage:", "").replace("query:", "")):
        vec[int(hashlib.md5(word.encode()).hexdigest(), 16) % settings.EMBEDDING_DIM] += 1.0
    norm = sum(x * x for x in vec) ** 0.5 or 1.0
    return [x / norm for x in vec]


@pytest.fixture(autouse=True)
def fake_embeddings(monkeypatch):
    """Keep tests fast and offline: replace the sentence-transformers model with a hashing embedder."""
    monkeypatch.setattr(embeddings, "embed_passages", lambda texts: [_fake_vector(t) for t in texts])
    monkeypatch.setattr(embeddings, "embed_query", _fake_vector)
