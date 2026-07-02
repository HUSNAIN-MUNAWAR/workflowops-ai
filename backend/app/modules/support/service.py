from __future__ import annotations

from collections import Counter
from typing import Any
from app.llm.mock_provider import MockLLMProvider


def classify_ticket(ticket: dict[str, Any], provider: MockLLMProvider | None = None) -> dict[str, Any]:
    provider = provider or MockLLMProvider()
    text = f"{ticket.get('subject','')}\n{ticket.get('body','')}"
    llm = provider.complete("support_ticket_summarization", text).data
    issue_type = "billing" if "refund" in text.lower() or "payment" in text.lower() else "technical" if "bug" in text.lower() or "error" in text.lower() else "account" if "login" in text.lower() else "general"
    return {**llm, "issue_type": issue_type}


def run_support_workflow(ticket: dict[str, Any]) -> dict[str, Any]:
    c = classify_ticket(ticket)
    vip = bool(ticket.get("vip"))
    risk = c["escalation_risk"] + (20 if vip else 0)
    risk = min(100, risk)
    return {
        "ticket_id": ticket.get("id"),
        "customer": ticket.get("customer"),
        "customer_history": ticket.get("history", []),
        "classification": c,
        "risk_score": risk,
        "draft_response": "We are sorry for the issue. A senior support reviewer will verify the resolution before we reply.",
        "escalate_to_human": risk >= 50,
        "resolution_status": "escalated" if risk >= 50 else "draft_ready",
    }


def weekly_root_cause_report(results: list[dict[str, Any]]) -> dict[str, Any]:
    counts = Counter(r["classification"]["issue_type"] for r in results)
    escalated = sum(1 for r in results if r["escalate_to_human"])
    return {"total_tickets": len(results), "issue_type_counts": dict(counts), "escalated": escalated, "top_root_causes": counts.most_common(5)}
