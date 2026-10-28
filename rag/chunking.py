"""Deliberately basic chunking: fixed-size character windows with overlap."""


def chunk_text(text: str, size: int = 800, overlap: int = 150) -> list[str]:
    """Split ``text`` into windows of ``size`` characters sharing ``overlap`` characters.

    Whitespace is normalised first so PDF line breaks do not waste space.
    The window end is nudged back to the nearest space so words are not cut in half.
    """
    if size <= 0:
        raise ValueError("size must be positive")
    if not 0 <= overlap < size:
        raise ValueError("overlap must be >= 0 and smaller than size")

    text = " ".join(text.split())
    if not text:
        return []

    chunks, start = [], 0
    while start < len(text):
        end = min(start + size, len(text))
        if end < len(text):
            space = text.rfind(" ", start + size // 2, end)
            if space != -1:
                end = space
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end >= len(text):
            break
        start = max(end - overlap, start + 1)  # always move forward
    return chunks
