from __future__ import annotations

from typing import Any
from app.llm.mock_provider import MockLLMProvider

RISK_TERMS = ["penalty", "liquidated damages", "unlimited liability", "bank guarantee", "termination for convenience", "data residency"]


def extract_requirements(text: str, provider: MockLLMProvider | None = None) -> dict[str, Any]:
    provider = provider or MockLLMProvider()
    return provider.complete("rfp_requirement_extraction", text).data


def detect_risk_clauses(text: str) -> list[dict[str, str]]:
    lower = text.lower()
    return [{"term": term, "severity": "high" if term in {"unlimited liability", "liquidated damages"} else "medium"} for term in RISK_TERMS if term in lower]


def compliance_matrix(requirements: list[str], company_profile: dict[str, Any]) -> list[dict[str, Any]]:
    capabilities = " ".join(company_profile.get("capabilities", [])).lower()
    rows = []
    for idx, req in enumerate(requirements, start=1):
        supported = any(word in capabilities for word in req.lower().split() if len(word) > 5)
        rows.append({"id": f"REQ-{idx:03d}", "requirement": req, "status": "compliant" if supported else "needs_evidence", "owner": "Proposal Lead" if supported else "Solution Architect"})
    return rows


def bid_no_bid_score(matrix: list[dict[str, Any]], risks: list[dict[str, str]], missing_docs: list[str]) -> dict[str, Any]:
    compliant = sum(1 for row in matrix if row["status"] == "compliant")
    base = 60 + (compliant / max(len(matrix), 1)) * 25
    base -= len(risks) * 6
    base -= len(missing_docs) * 5
    score = round(max(0, min(100, base)), 2)
    return {"score": score, "recommendation": "bid" if score >= 70 else "conditional_bid" if score >= 50 else "no_bid"}


def run_rfp_workflow(text: str, company_profile: dict[str, Any]) -> dict[str, Any]:
    extracted = extract_requirements(text)
    reqs = extracted.get("requirements", [])
    mandatory_docs = extracted.get("mandatory_documents", [])
    provided_docs = set(company_profile.get("documents", []))
    missing_docs = [doc for doc in mandatory_docs if doc not in provided_docs]
    risks = detect_risk_clauses(text)
    matrix = compliance_matrix(reqs, company_profile)
    score = bid_no_bid_score(matrix, risks, missing_docs)
    return {
        "requirements": reqs,
        "mandatory_documents": mandatory_docs,
        "missing_documents": missing_docs,
        "risk_clauses": risks,
        "compliance_matrix": matrix,
        "bid_no_bid": score,
        "proposal_outline": ["Executive Summary", "Understanding of Requirements", "Solution Architecture", "Implementation Plan", "Compliance Matrix", "Commercials", "Appendices"],
        "submission_checklist": mandatory_docs + ["technical proposal", "commercial proposal", "signed forms"],
    }
