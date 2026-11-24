from __future__ import annotations

import json
from typing import Any
import httpx
from app.llm.base import LLMProvider, LLMResponse


class OpenAIProvider(LLMProvider):
    name = "openai"

    def __init__(self, api_key: str | None = None, base_url: str = "https://api.openai.com/v1", timeout_seconds: float = 60.0) -> None:
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds

    def complete(self, task: str, prompt: str, **kwargs: Any) -> LLMResponse:
        if not self.api_key:
            raise RuntimeError("OPENAI_API_KEY is not configured. Use MockLLMProvider for local demo.")
        model = str(kwargs.get("model") or "gpt-4o-mini")
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": "Return one valid JSON object with task-specific fields and a concise explanation."},
                {"role": "user", "content": f"Task: {task}\n\n{prompt}"},
            ],
            "temperature": float(kwargs.get("temperature", 0.0)),
            "max_tokens": int(kwargs.get("max_tokens", 1200)),
            "response_format": {"type": "json_object"},
        }
        try:
            with httpx.Client(timeout=self.timeout_seconds) as client:
                response = client.post(
                    f"{self.base_url}/chat/completions",
                    headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
                    json=payload,
                )
                response.raise_for_status()
                body = response.json()
            text = body["choices"][0]["message"]["content"]
        except (httpx.HTTPError, ValueError, KeyError, IndexError, TypeError) as exc:
            raise RuntimeError(f"OpenAI provider request failed: {exc}") from exc
        if not isinstance(text, str) or not text.strip():
            raise RuntimeError("OpenAI provider returned an empty response")
        data = _structured_data(text)
        usage = body.get("usage", {}) if isinstance(body, dict) else {}
        if isinstance(usage, dict):
            data["_usage"] = usage
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
