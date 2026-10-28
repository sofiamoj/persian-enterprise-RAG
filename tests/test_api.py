import io
import json

import pytest
from django.test import Client

from rag import llm
from rag.ingest import ingest

pytestmark = pytest.mark.django_db


@pytest.fixture
def docs():
    ingest("plants.txt", io.BytesIO(b"photosynthesis turns sunlight into glucose and oxygen"))
    ingest("fable.txt", io.BytesIO(b"the tortoise beat the hare in a race"))


def post(payload, raw=False):
    return Client().post("/api/ask", payload if raw else json.dumps(payload), content_type="application/json")


def test_without_api_key_returns_chunks_only(docs, settings):
    settings.OPENAI_API_KEY = ""
    data = post({"question": "what does photosynthesis make?"}).json()
    assert data["answer"] is None and "chunks only" in data["note"]
    assert data["sources"][0]["document"] == "plants.txt"
    assert {"document", "chunk", "text", "score"} <= data["sources"][0].keys()


def test_with_api_key_includes_llm_answer(docs, settings, monkeypatch):
    settings.OPENAI_API_KEY = "test-key"
    seen = {}

    def fake_generate(question, sources):
        seen["sources"] = sources
        return "Glucose and oxygen [1]."

    monkeypatch.setattr(llm, "generate_answer", fake_generate)
    data = post({"question": "what does photosynthesis make?"}).json()
    assert data["answer"] == "Glucose and oxygen [1]." and data["note"] is None
    assert seen["sources"][0]["document"] == "plants.txt"


def test_llm_failure_falls_back_to_chunks(docs, settings, monkeypatch):
    settings.OPENAI_API_KEY = "test-key"

    def boom(question, sources):
        raise RuntimeError("network down")

    monkeypatch.setattr(llm, "generate_answer", boom)
    data = post({"question": "photosynthesis"}).json()
    assert data["answer"] is None and "RuntimeError" in data["note"] and data["sources"]


def test_empty_index_returns_note():
    data = post({"question": "anything"}).json()
    assert data["sources"] == [] and "Upload" in data["note"]


@pytest.mark.parametrize("payload,raw", [({"question": "  "}, False), ({}, False), ("not json", True)])
def test_bad_requests_get_400(payload, raw):
    assert post(payload, raw).status_code == 400


def test_get_not_allowed():
    assert Client().get("/api/ask").status_code == 405


def test_web_ui_upload_and_ask(settings):
    settings.OPENAI_API_KEY = ""
    client = Client()
    f = io.BytesIO("حافظ در شیراز آرمیده است".encode("utf-8"))
    f.name = "hafez.txt"
    assert "Indexed hafez.txt" in client.post("/", {"files": f}).content.decode()
    html = client.post("/", {"question": "حافظ کجاست؟"}).content.decode()
    assert "hafez.txt" in html and 'dir="auto"' in html
