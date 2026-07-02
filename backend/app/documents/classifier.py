from __future__ import annotations
from dataclasses import dataclass

@dataclass
class DocumentClassification:
    document_type: str
    confidence: float
    reasons: list[str]

KEYWORDS = {
    "invoice": ["invoice", "amount due", "tax", "due date", "vendor"],
    "purchase_order": ["purchase order", "po number", "buyer", "supplier"],
    "rfp": ["rfp", "request for proposal", "tender", "bid", "mandatory", "deadline"],
    "contract": ["agreement", "clause", "party", "term", "contract"],
    "policy_document": ["policy", "control", "iso", "soc 2", "audit"],
    "support_attachment": ["ticket", "refund", "support", "customer", "vip", "outage"],
}

def classify_document(text: str) -> DocumentClassification:
    low = (text or "").lower()
    best = ("general_business_document", 0, [])
    for doc_type, words in KEYWORDS.items():
        hits = [w for w in words if w in low]
        if len(hits) > best[1]:
            best = (doc_type, len(hits), hits)
    if best[1] == 0:
        return DocumentClassification("general_business_document", 0.35, ["No strong business-document keyword match"])
    return DocumentClassification(best[0], round(min(0.95, 0.45 + 0.1 * best[1]), 2), [f"Matched: {', '.join(best[2])}"])
