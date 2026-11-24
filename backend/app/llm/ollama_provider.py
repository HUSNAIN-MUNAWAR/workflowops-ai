from __future__ import annotations

import json
from typing import Any
import httpx
from app.llm.base import LLMProvider, LLMResponse


class OllamaProvider(LLMProvider):
    name = "ollama"

    def __init__(self, base_url: str = "http://localhost:11434", timeout_seconds: float = 120.0) -> None:
        self.base_url = base_url
        self.timeout_seconds = timeout_seconds

    def complete(self, task: str, prompt: str, **kwargs: Any) -> LLMResponse:
        model = str(kwargs.get("model") or "llama3.1")
        payload = {
            "model": model,
            "prompt": f"Return one valid JSON object.\nTask: {task}\n\n{prompt}",
            "stream": False,
            "format": "json",
            "options": {"temperature": float(kwargs.get("temperature", 0.0))},
        }
        try:
            with httpx.Client(timeout=self.timeout_seconds) as client:
                response = client.post(f"{self.base_url.rstrip('/')}/api/generate", json=payload)
                response.raise_for_status()
                body = response.json()
            text = body.get("response") if isinstance(body, dict) else None
        except (httpx.HTTPError, ValueError, TypeError) as exc:
            raise RuntimeError(f"Ollama provider request failed: {exc}") from exc
        if not isinstance(text, str) or not text.strip():
            raise RuntimeError("Ollama provider returned an empty response")
        data = _structured_data(text)
        return LLMResponse(text=text, data=data, provider=self.name, deterministic=False, confidence=float(data.get("confidence", 0.0) or 0.0))


def _structured_data(text: str) -> dict[str, Any]:
    candidate = text.strip()
    if candidate.startswith("```"):
        candidate = candidate.strip("`").removeprefix("json").strip()
    try:
        parsed = json.loads(candidate)
    except json.JSONDecodeError:
        return {"raw_response": text}
    return parsed if isinstance(parsed, dict) else {"result": parsed}
