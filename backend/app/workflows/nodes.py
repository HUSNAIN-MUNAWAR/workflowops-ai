from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class NodeStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    WAITING_APPROVAL = "waiting_approval"


@dataclass
class WorkflowNode:
    node_id: str
    node_type: str
    name: str
    config: dict[str, Any] = field(default_factory=dict)
    retry_limit: int = 1
    requires_approval: bool = False


@dataclass
class NodeResult:
    node_id: str
    status: NodeStatus
    output: dict[str, Any]
    error: str | None = None
    attempts: int = 1
