from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any
import re

@dataclass
class ExtractionResult:
    fields: dict[str, Any]
    confidence: float
    warnings: list[str] = field(default_factory=list)
    required_fields: list[str] = field(default_factory=list)

FIELD_PATTERNS = {
    "invoice_number": re.compile(r"(?i)(invoice\s*(no\.?|number|#)|\binv\b\s*(?:#|no\.?)?)\s*[:]\s*([A-Z0-9\-\/]+)"),
    "po_number": re.compile(r"(?i)(po\s*(no\.?|number|#)|purchase\s*order)\s*[:\-]?\s*([A-Z0-9\-\/]+)"),
    "vendor": re.compile(r"(?i)(vendor|supplier|from)\s*[:\-]?\s*([A-Za-z0-9 &.,'\-]+)"),
    "total": re.compile(r"(?i)(total\s*(amount)?|amount\s*due|grand\s*total)\s*[:\-]?\s*(PKR|USD|SAR|AED|EUR|GBP)?\s*([0-9,]+(?:\.\d{1,2})?)"),
    "tax": re.compile(r"(?i)(tax|vat|gst)\s*[:\-]?\s*(PKR|USD|SAR|AED|EUR|GBP)?\s*([0-9,]+(?:\.\d{1,2})?)"),
    "currency": re.compile(r"\b(PKR|USD|SAR|AED|EUR|GBP)\b"),
    "due_date": re.compile(r"(?i)(due\s*date|payment\s*due)\s*[:\-]?\s*([0-9]{4}-[0-9]{2}-[0-9]{2}|[0-9]{1,2}[\/\-][0-9]{1,2}[\/\-][0-9]{2,4})"),
    "deadline": re.compile(r"(?i)(deadline|submission\s*date|closing\s*date)\s*[:\-]?\s*([0-9]{4}-[0-9]{2}-[0-9]{2}|[0-9]{1,2}[\/\-][0-9]{1,2}[\/\-][0-9]{2,4})"),
    "control_id": re.compile(r"\b((?:ISO|SOC|CTRL|CC|A)\-?[0-9]{1,3}(?:\.[0-9])?)\b", re.I),
}
MANDATORY_RE = re.compile(r"(?im)^\s*(?:mandatory|required|must provide|shall include)[:\-]?\s*(.+)$")
REQ_BULLET_RE = re.compile(r"(?im)^\s*(?:\-|\*|\d+\.)\s*(must|shall|required|mandatory)\b(.+)$")


def _clean(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip(" .;,\n\t")


def _amount(value: str) -> float | None:
    try:
        return float(value.replace(',', ''))
    except Exception:
        return None


def extract_key_values(text: str) -> dict[str, Any]:
    text = text or ""
    fields: dict[str, Any] = {}
    for name, pattern in FIELD_PATTERNS.items():
        match = pattern.search(text)
        if not match:
            continue
        if name in {"invoice_number", "po_number"}:
            fields[name] = _clean(match.group(3))
        elif name == "vendor":
            fields[name] = _clean(match.group(2))
        elif name == "total":
            if match.group(3): fields.setdefault("currency", match.group(3).upper())
            fields[name] = _amount(match.group(4))
        elif name == "tax":
            if match.group(2): fields.setdefault("currency", match.group(2).upper())
            fields[name] = _amount(match.group(3))
        elif name == "currency":
            fields.setdefault("currency", match.group(1).upper())
        elif name in {"due_date", "deadline"}:
            fields[name] = _clean(match.group(2))
        elif name == "control_id":
            fields[name] = _clean(match.group(1)).upper()
    mandatory = [_clean(m.group(1)) for m in MANDATORY_RE.finditer(text)]
    bullets = [_clean((m.group(1) + " " + m.group(2))) for m in REQ_BULLET_RE.finditer(text)]
    if mandatory or bullets:
        fields["mandatory_requirements"] = (mandatory + bullets)[:20]
        fields["mandatory_documents"] = [x for x in mandatory + bullets if any(k in x.lower() for k in ["certificate", "document", "profile", "license", "audit", "financial"])]
    if any(k in text.lower() for k in ["refund", "angry", "legal", "vip", "urgent", "breach"]):
        fields["support_risk_terms"] = [k for k in ["refund", "angry", "legal", "vip", "urgent", "breach"] if k in text.lower()]
    return fields


def confidence_score(fields: dict[str, Any], required: list[str]) -> float:
    if not required:
        return 0.70 if fields else 0.35
    present = sum(1 for key in required if fields.get(key) not in [None, "", []])
    base = present / len(required)
    return 1.0 if present == len(required) else round(max(0.05, min(0.99, 0.2 + base * 0.75)), 2)


def extract_for_document_type(text: str, document_type: str) -> ExtractionResult:
    required = {
        "invoice": ["vendor", "invoice_number", "total", "due_date"],
        "purchase_order": ["po_number", "vendor", "total"],
        "rfp": ["deadline", "mandatory_requirements"],
        "policy_document": ["control_id"],
        "support_attachment": ["support_risk_terms"],
    }.get(document_type, [])
    fields = extract_key_values(text)
    warnings = [f"Missing required field: {k}" for k in required if not fields.get(k)]
    if "ignore previous instructions" in text.lower() or "bypass approval" in text.lower():
        warnings.append("Potential prompt injection text detected; extraction should be reviewed.")
    return ExtractionResult(fields=fields, confidence=confidence_score(fields, required), warnings=warnings, required_fields=required)
