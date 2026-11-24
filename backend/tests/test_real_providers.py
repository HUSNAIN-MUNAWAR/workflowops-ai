import httpx
import pytest

from app.llm import get_provider
from app.llm.openai_provider import OpenAIProvider
from app.llm.ollama_provider import OllamaProvider


def test_openai_provider_executes_openai_compatible_response(monkeypatch):
    class Response:
        def raise_for_status(self):
            return None

        def json(self):
            return {"choices": [{"message": {"content": '{"decision":"approve","confidence":0.9}'}}], "usage": {"total_tokens": 4}}

    class Client:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def post(self, url, **kwargs):
            assert url.endswith("/chat/completions")
            assert kwargs["json"]["model"] == "test-model"
            return Response()

    monkeypatch.setattr(httpx, "Client", lambda *args, **kwargs: Client())
    result = OpenAIProvider("test-key", "http://provider.test").complete("policy", "approve", model="test-model")
    assert result.provider == "openai"
    assert result.data["decision"] == "approve"
    assert result.deterministic is False


def test_ollama_provider_executes_json_response(monkeypatch):
    class Response:
        def raise_for_status(self):
            return None

        def json(self):
            return {"response": '{"status":"recovered"}'}

    class Client:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def post(self, url, **kwargs):
            assert url.endswith("/api/generate")
            return Response()

    monkeypatch.setattr(httpx, "Client", lambda *args, **kwargs: Client())
    result = OllamaProvider("http://ollama.test").complete("recovery", "retry", model="tinyllama")
    assert result.provider == "ollama"
    assert result.data["status"] == "recovered"
    assert result.deterministic is False


def test_real_provider_failure_does_not_fall_back_to_mock(monkeypatch):
    def fail(*args, **kwargs):
        raise httpx.ConnectError("offline")

    monkeypatch.setattr(httpx, "Client", fail)
    with pytest.raises(RuntimeError, match="Ollama provider request failed"):
        get_provider("ollama").complete("task", "prompt")
