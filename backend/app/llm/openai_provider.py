from __future__ import annotations

from typing import Any
from app.llm.base import LLMProvider, LLMResponse


class OpenAIProvider(LLMProvider):
    name = "openai"

    def __init__(self, api_key: str | None = None) -> None:
        self.api_key = api_key

    def complete(self, task: str, prompt: str, **kwargs: Any) -> LLMResponse:
        if not self.api_key:
            raise RuntimeError("OPENAI_API_KEY is not configured. Use MockLLMProvider for local demo.")
        # Integration placeholder: intentionally not called in demo/test mode.
        raise NotImplementedError("Wire the official OpenAI client here for production deployments.")
