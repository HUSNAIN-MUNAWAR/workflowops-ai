from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


@dataclass
class AuditEvent:
    event_id: str
    actor: str
    action: str
    target: str
    details: dict[str, Any]
    created_at: str


@dataclass
class AuditLogger:
    events: list[AuditEvent] = field(default_factory=list)

    def record(self, actor: str, action: str, target: str, **details: Any) -> AuditEvent:
        event = AuditEvent(
            event_id=str(uuid4()),
            actor=actor,
            action=action,
            target=target,
            details=details,
            created_at=datetime.now(timezone.utc).isoformat(),
        )
        self.events.append(event)
        return event

    def as_dicts(self) -> list[dict[str, Any]]:
        return [event.__dict__ for event in self.events]
