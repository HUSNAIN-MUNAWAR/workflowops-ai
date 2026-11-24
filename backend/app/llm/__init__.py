from app.llm.mock_provider import MockLLMProvider
from app.llm.openai_provider import OpenAIProvider
from app.llm.ollama_provider import OllamaProvider


def get_provider(name: str = "mock", **kwargs):
    if name == "mock":
        return MockLLMProvider()
    if name == "openai":
        return OpenAIProvider(
            api_key=kwargs.get("api_key"),
            base_url=kwargs.get("base_url", "https://api.openai.com/v1"),
            timeout_seconds=float(kwargs.get("timeout_seconds", 60.0)),
        )
    if name == "ollama":
        return OllamaProvider(
            base_url=kwargs.get("base_url", "http://localhost:11434"),
            timeout_seconds=float(kwargs.get("timeout_seconds", 120.0)),
        )
    raise ValueError(f"Unknown provider: {name}")
