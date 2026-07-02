from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any
from app.llm.mock_provider import MockLLMProvider


def classify_email(email: dict[str, Any], provider: MockLLMProvider | None = None) -> dict[str, Any]:
    provider = provider or MockLLMProvider()
    text = f"Subject: {email.get('subject','')}\nFrom: {email.get('sender','')}\n{email.get('body','')}"
    result = provider.complete("email_classification", text).data
    return result


def sla_due_at(category: str, urgency: str) -> str:
    hours = 4 if urgency == "high" else 12 if category in {"complaint", "support_issue"} else 24
    return (datetime.now(timezone.utc) + timedelta(hours=hours)).isoformat()


def urgency_score(category: str, urgency: str, body: str) -> int:
    score = {"normal": 25, "medium": 45, "high": 75}.get(urgency, 30)
    if any(w in body.lower() for w in ["legal", "refund", "breach", "angry"]):
        score += 15
    if category == "spam_low_priority":
        score = min(score, 10)
    return min(score, 100)


def draft_reply(email: dict[str, Any], classification: dict[str, Any]) -> str:
    return (
        f"Hi,\n\nThanks for your message about {classification['category'].replace('_', ' ')}. "
        "We have created an internal task and a reviewer will verify the next action before anything is sent externally."
        "\n\nRegards,\nWorkflowOps Demo Team"
    )


def run_email_workflow(email: dict[str, Any]) -> dict[str, Any]:
    c = classify_email(email)
    score = urgency_score(c["category"], c["urgency"], email.get("body", ""))
    return {
        "email_id": email.get("id"),
        "classification": c,
        "entities": {
            "sender": email.get("sender"),
            "company": email.get("company", "Unknown"),
            "deadline": email.get("deadline"),
            "requested_action": c.get("requested_action"),
        },
        "task": {
            "title": f"Handle {c['category'].replace('_',' ')} from {email.get('sender')}",
            "department": c["department"],
            "sla_due_at": sla_due_at(c["category"], c["urgency"]),
            "status": "open",
        },
        "urgency_score": score,
        "draft_reply": draft_reply(email, c),
        "requires_approval_before_send": True,
        "status": "needs_human_review" if c["category"] == "ambiguous_review" or score >= 70 else "task_created",
    }


def daily_inbox_summary(results: list[dict[str, Any]]) -> dict[str, Any]:
    by_category: dict[str, int] = {}
    pending_approval = 0
    for r in results:
        cat = r["classification"]["category"]
        by_category[cat] = by_category.get(cat, 0) + 1
        if r.get("requires_approval_before_send"):
            pending_approval += 1
    return {"total": len(results), "by_category": by_category, "pending_approval": pending_approval}
