from . import llm
from .retrieval import retrieve


def ask(question: str) -> dict:
    """Retrieve sources; add an LLM answer when an API key is configured."""
    sources = retrieve(question)
    answer, note = None, None
    if not sources:
        note = "No documents indexed yet. Upload one first."
    elif llm.llm_enabled():
        try:
            answer = llm.generate_answer(question, sources)
        except Exception as exc:  # network/auth errors should not hide the retrieved chunks
            note = f"LLM call failed ({type(exc).__name__}); showing retrieved chunks only."
    else:
        note = "No OPENAI_API_KEY set; showing retrieved chunks only."
    return {"question": question, "answer": answer, "note": note, "sources": sources}
