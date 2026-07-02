from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


@dataclass
class ApprovalRequest:
    title: str
    reason: str
    risk_score: float
    requested_by: str = "workflow_engine"
    reviewer_role: str = "reviewer"
    status: str = "pending"
    approval_id: str = field(default_factory=lambda: str(uuid4()))
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    decision_reason: str | None = None


def should_request_approval(risk_score: float, threshold: float, action_type: str = "internal") -> bool:
    external_or_sensitive = action_type in {"external_email", "payment_export", "legal_response", "customer_refund"}
    return risk_score >= threshold or external_or_sensitive


def decide_approval(request: ApprovalRequest, decision: str, reason: str) -> ApprovalRequest:
    if decision not in {"approved", "rejected", "revise"}:
        raise ValueError("Decision must be approved, rejected, or revise")
    request.status = decision
    request.decision_reason = reason
    return request
