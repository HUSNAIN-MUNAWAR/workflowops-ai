from __future__ import annotations

from typing import Any


def build_replay(events: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "event_count": len(events),
        "timeline": events,
        "first_failure": next((e for e in events if e.get("status") == "failed"), None),
    }
