from __future__ import annotations

import hashlib
import re
from typing import Any
from app.llm.base import LLMProvider, LLMResponse


class MockLLMProvider(LLMProvider):
    """Deterministic provider used for reproducible demos and tests.

    This is intentionally not a fake claim of model accuracy. It returns useful,
    rule-based outputs for synthetic examples so the platform can run without paid APIs.
    """

    name = "mock"

    def complete(self, task: str, prompt: str, **kwargs: Any) -> LLMResponse:
        seed = hashlib.sha256(f"{task}:{prompt[:500]}".encode()).hexdigest()[:10]
        task_key = task.lower()
        if "invoice" in task_key:
            data = self._invoice(prompt)
            text = f"Extracted invoice fields with deterministic rule set {seed}."
        elif "email" in task_key:
            data = self._email(prompt)
            text = f"Classified email as {data['category']} with {data['urgency']} urgency."
        elif "rfp" in task_key or "tender" in task_key:
            data = self._rfp(prompt)
            text = "Extracted requirements and generated compliance matrix draft."
        elif "support" in task_key:
            data = self._support(prompt)
            text = "Summarized ticket and estimated escalation risk."
        elif "compliance" in task_key:
            data = self._compliance(prompt)
            text = "Mapped synthetic evidence to controls."
        elif "reliability" in task_key:
            data = {"explanation": "Scenario failed because a safety or validation guard was triggered.", "mitigation": "Add validation, approval gate, retry limits, and replay logs."}
            text = data["explanation"]
        else:
            data = {"summary": prompt[:160], "seed": seed}
            text = "Deterministic mock completion."
        return LLMResponse(text=text, data=data, provider=self.name, deterministic=True, confidence=0.82)

    def _invoice(self, text: str) -> dict[str, Any]:
        amount = re.search(r"(?:total|amount)\s*[:=]\s*([A-Z]{3})?\s*([0-9,.]+)", text, re.I)
        invoice_no = re.search(r"invoice\s*(?:number|no|#)\s*[:=]\s*([A-Z0-9-]+)", text, re.I)
        vendor = re.search(r"vendor\s*[:=]\s*([^\n]+)", text, re.I)
        due = re.search(r"due\s*date\s*[:=]\s*([0-9\-/]+)", text, re.I)
        return {
            "vendor_name": vendor.group(1).strip() if vendor else "Unknown Vendor",
            "invoice_number": invoice_no.group(1) if invoice_no else "UNKNOWN",
            "amount": float(amount.group(2).replace(',', '')) if amount else 0.0,
            "currency": amount.group(1) if amount and amount.group(1) else "USD",
            "due_date": due.group(1) if due else None,
            "tax": 0.0,
            "confidence": 0.78 if amount and invoice_no else 0.42,
        }

    def _email(self, text: str) -> dict[str, Any]:
        lower = text.lower()
        if "invoice" in lower or "payment" in lower:
            cat = "invoice"
        elif "refund" in lower or "angry" in lower or "legal" in lower:
            cat = "complaint"
        elif "proposal" in lower or "rfp" in lower or "tender" in lower:
            cat = "sales_lead"
        elif "login" in lower or "bug" in lower or "support" in lower:
            cat = "support_issue"
        elif "hr" in lower or "leave" in lower:
            cat = "hr_request"
        elif "partnership" in lower:
            cat = "partnership"
        elif "unsubscribe" in lower or "lottery" in lower:
            cat = "spam_low_priority"
        else:
            cat = "ambiguous_review"
        urgency = "high" if any(w in lower for w in ["urgent", "today", "breach", "legal", "angry"]) else "medium" if "tomorrow" in lower else "normal"
        return {"category": cat, "urgency": urgency, "requested_action": "review and respond", "department": self._department(cat)}

    def _department(self, cat: str) -> str:
        return {
            "invoice": "Finance",
            "complaint": "Customer Success",
            "sales_lead": "Sales",
            "support_issue": "Support",
            "hr_request": "HR",
            "partnership": "Partnerships",
            "spam_low_priority": "Inbox Ops",
        }.get(cat, "Operations")

    def _rfp(self, text: str) -> dict[str, Any]:
        reqs = []
        for line in text.splitlines():
            l = line.strip(" -*")
            if any(k in l.lower() for k in ["must", "shall", "required", "mandatory", "certificate", "deadline"]):
                reqs.append(l)
        return {"requirements": reqs[:20], "mandatory_documents": [r for r in reqs if "certificate" in r.lower()], "bid_score": 72 if reqs else 45}

    def _support(self, text: str) -> dict[str, Any]:
        lower = text.lower()
        risk_terms = ["angry", "refund", "legal", "cancel", "vip", "breach", "lawsuit"]
        hits = [t for t in risk_terms if t in lower]
        return {"summary": text[:240], "risk_terms": hits, "escalation_risk": min(100, 20 + 18*len(hits)), "recommended_action": "human escalation" if hits else "standard support response"}

    def _compliance(self, text: str) -> dict[str, Any]:
        return {"mapped_controls": 3, "missing_evidence": ["reviewer approval", "latest CI log"] if "missing" in text.lower() else [], "coverage_score": 76}
