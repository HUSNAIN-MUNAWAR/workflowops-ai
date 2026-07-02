from __future__ import annotations

from typing import Any
from app.llm.base import LLMProvider, LLMResponse


class OllamaProvider(LLMProvider):
    name = "ollama"

    def __init__(self, base_url: str = "http://localhost:11434") -> None:
        self.base_url = base_url

    def complete(self, task: str, prompt: str, **kwargs: Any) -> LLMResponse:
        # Integration placeholder: keep demo deterministic unless a user enables Ollama.
        raise NotImplementedError("Ollama execution is optional; MockLLMProvider is the default demo provider.")
