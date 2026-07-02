from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Any


def configure_logging(level: int = logging.INFO) -> None:
    logging.basicConfig(level=level, format="%(message)s")


def log_event(logger: logging.Logger, event: str, **payload: Any) -> None:
    record = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "event": event,
        **payload,
    }
    logger.info(json.dumps(record, default=str))
