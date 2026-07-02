from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any
from app.llm.mock_provider import MockLLMProvider

REQUIRED_INVOICE_FIELDS = ["vendor_name", "invoice_number", "amount", "currency", "due_date"]


def load_vendor_master(path: str | Path) -> list[dict[str, str]]:
    with Path(path).open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def parse_invoice_text(text: str, provider: MockLLMProvider | None = None) -> dict[str, Any]:
    provider = provider or MockLLMProvider()
    extracted = provider.complete("invoice_extraction", text).data
    missing = [field for field in REQUIRED_INVOICE_FIELDS if not extracted.get(field)]
    extracted["missing_fields"] = missing
    return extracted


def detect_duplicate(invoice: dict[str, Any], previous: list[dict[str, Any]]) -> bool:
    return any(
        row.get("invoice_number") == invoice.get("invoice_number") and row.get("vendor_name", "").lower() == invoice.get("vendor_name", "").lower()
        for row in previous
    )


def match_purchase_order(invoice: dict[str, Any], po: dict[str, Any]) -> dict[str, Any]:
    amount_delta = abs(float(invoice.get("amount", 0)) - float(po.get("amount", 0)))
    vendor_match = invoice.get("vendor_name", "").lower() in po.get("vendor_name", "").lower() or po.get("vendor_name", "").lower() in invoice.get("vendor_name", "").lower()
    return {
        "vendor_match": vendor_match,
        "amount_match": amount_delta <= float(po.get("tolerance", 5.0)),
        "amount_delta": round(amount_delta, 2),
        "po_number": po.get("po_number"),
    }


def invoice_risk_score(invoice: dict[str, Any], duplicate: bool, po_match: dict[str, Any], approval_limit: float = 5000.0) -> dict[str, Any]:
    score = 10
    reasons: list[str] = []
    if invoice.get("missing_fields"):
        score += 25; reasons.append("missing required fields")
    if duplicate:
        score += 35; reasons.append("duplicate invoice detected")
    if not po_match.get("vendor_match"):
        score += 20; reasons.append("vendor mismatch")
    if not po_match.get("amount_match"):
        score += 20; reasons.append("amount mismatch")
    if float(invoice.get("amount", 0)) > approval_limit:
        score += 20; reasons.append("amount exceeds approval limit")
    return {"score": min(score, 100), "level": "high" if score >= 70 else "medium" if score >= 40 else "low", "reasons": reasons}


def run_invoice_workflow(invoice_text: str, po: dict[str, Any], vendor_master: list[dict[str, str]], previous_invoices: list[dict[str, Any]]) -> dict[str, Any]:
    invoice = parse_invoice_text(invoice_text)
    duplicate = detect_duplicate(invoice, previous_invoices)
    po_match = match_purchase_order(invoice, po)
    risk = invoice_risk_score(invoice, duplicate, po_match)
    vendor_known = any(v["vendor_name"].lower() == invoice["vendor_name"].lower() for v in vendor_master)
    exception = risk["score"] >= 40 or not vendor_known
    approval_chain = ["finance_reviewer"] + (["finance_manager"] if invoice.get("amount", 0) > 5000 else [])
    return {
        "invoice": invoice,
        "vendor_known": vendor_known,
        "duplicate": duplicate,
        "po_match": po_match,
        "risk": risk,
        "approval_chain": approval_chain,
        "status": "exception" if exception else "payment_ready",
        "payment_export": {
            "vendor_name": invoice.get("vendor_name"),
            "invoice_number": invoice.get("invoice_number"),
            "amount": invoice.get("amount"),
            "currency": invoice.get("currency"),
            "due_date": invoice.get("due_date"),
        } if not exception else None,
    }
