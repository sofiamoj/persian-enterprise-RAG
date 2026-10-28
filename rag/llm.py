"""Answer generation through any OpenAI-compatible chat API."""
from django.conf import settings

SYSTEM_PROMPT = (
    "Answer the question using only the numbered context passages. "
    "Reply in the language of the question and cite passages like [1]. "
    "If the context does not contain the answer, say you don't know."
)


def llm_enabled() -> bool:
    return bool(settings.OPENAI_API_KEY)


def generate_answer(question: str, sources: list[dict]) -> str:
    from openai import OpenAI

    client = OpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_BASE_URL)
    context = "\n\n".join(
        f"[{i}] ({s['document']}, chunk {s['chunk']})\n{s['text']}" for i, s in enumerate(sources, 1)
    )
    response = client.chat.completions.create(
        model=settings.OPENAI_MODEL,
        temperature=0,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"},
        ],
    )
    return response.choices[0].message.content.strip()
