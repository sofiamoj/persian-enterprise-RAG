from django.conf import settings
from pgvector.django import CosineDistance

from . import embeddings
from .models import Chunk


def retrieve(question: str, k: int | None = None) -> list[dict]:
    """Top-k chunks by cosine similarity (pgvector). Score = 1 - cosine distance."""
    qvec = embeddings.embed_query(question)
    hits = (
        Chunk.objects.select_related("document")
        .annotate(distance=CosineDistance("embedding", qvec))
        .order_by("distance")[: k or settings.TOP_K]
    )
    return [
        {
            "document": c.document.name,
            "chunk": c.index + 1,  # 1-based for humans
            "text": c.text,
            "score": round(1 - c.distance, 4),
        }
        for c in hits
    ]
