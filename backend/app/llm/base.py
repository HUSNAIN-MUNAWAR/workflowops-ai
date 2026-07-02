from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass
class LLMResponse:
    text: str
    data: dict[str, Any]
    provider: str
    deterministic: bool
    confidence: float


class LLMProvider(ABC):
    name: str

    @abstractmethod
    def complete(self, task: str, prompt: str, **kwargs: Any) -> LLMResponse:
        raise NotImplementedError
