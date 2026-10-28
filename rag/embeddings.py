"""Local multilingual-e5-small embeddings (no API key). E5 needs 'query: ' / 'passage: ' prefixes."""
from functools import lru_cache

from django.conf import settings


@lru_cache(maxsize=1)
def _model():
    from sentence_transformers import SentenceTransformer  # heavy import, load lazily

    return SentenceTransformer(settings.EMBEDDING_MODEL)


def _encode(texts: list[str], prefix: str) -> list[list[float]]:
    vectors = _model().encode([prefix + t for t in texts], normalize_embeddings=True)
    return [v.tolist() for v in vectors]


def embed_passages(texts: list[str]) -> list[list[float]]:
    return _encode(texts, "passage: ")


def embed_query(text: str) -> list[float]:
    return _encode([text], "query: ")[0]
