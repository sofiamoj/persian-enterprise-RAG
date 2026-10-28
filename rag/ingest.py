"""Extract text from .txt/.pdf/.docx, chunk it, embed it, store it."""
from pathlib import Path

from django.conf import settings
from django.db import transaction

from . import embeddings
from .chunking import chunk_text
from .models import Chunk, Document

SUPPORTED = {".txt", ".pdf", ".docx"}


def extract_text(name: str, fileobj) -> str:
    ext = Path(name).suffix.lower()
    if ext == ".txt":
        raw = fileobj.read()
        for enc in ("utf-8-sig", "utf-16", "cp1256"):  # cp1256 = legacy Windows Arabic/Persian
            try:
                return raw.decode(enc)
            except UnicodeDecodeError:
                continue
        return raw.decode("utf-8", errors="replace")
    if ext == ".pdf":
        from pypdf import PdfReader

        return "\n".join(page.extract_text() or "" for page in PdfReader(fileobj).pages)
    if ext == ".docx":
        from docx import Document as DocxDocument

        return "\n".join(p.text for p in DocxDocument(fileobj).paragraphs)
    raise ValueError(f"Unsupported file type '{ext}'. Use .txt, .pdf or .docx.")


def ingest(name: str, fileobj) -> Document:
    """Store one document. Raises ValueError if it is unsupported or has no text."""
    pieces = chunk_text(extract_text(name, fileobj), settings.CHUNK_SIZE, settings.CHUNK_OVERLAP)
    if not pieces:
        raise ValueError(f"No extractable text in '{name}'.")
    vectors = embeddings.embed_passages(pieces)
    with transaction.atomic():
        doc = Document.objects.create(name=name)
        Chunk.objects.bulk_create(
            Chunk(document=doc, index=i, text=t, embedding=v)
            for i, (t, v) in enumerate(zip(pieces, vectors))
        )
    return doc
