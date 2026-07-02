from __future__ import annotations

from typing import Any


def map_evidence_to_controls(controls: list[dict[str, Any]], evidence: list[dict[str, Any]]) -> list[dict[str, Any]]:
    mapped = []
    for control in controls:
        keywords = {k.lower() for k in control.get("keywords", [])}
        matches = []
        for ev in evidence:
            blob = f"{ev.get('title','')} {ev.get('type','')} {ev.get('summary','')}".lower()
            if any(k in blob for k in keywords):
                matches.append(ev)
        mapped.append({"control_id": control["control_id"], "control": control["title"], "evidence": matches, "covered": bool(matches)})
    return mapped


def coverage_score(mapping: list[dict[str, Any]]) -> float:
    if not mapping:
        return 0.0
    return round(100 * sum(1 for row in mapping if row["covered"]) / len(mapping), 2)


def missing_evidence_tasks(mapping: list[dict[str, Any]]) -> list[dict[str, str]]:
    return [{"title": f"Collect evidence for {row['control_id']}", "owner": "Compliance Reviewer", "status": "open"} for row in mapping if not row["covered"]]


def evidence_timeline(evidence: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted([{"date": ev.get("date"), "title": ev.get("title"), "type": ev.get("type")} for ev in evidence], key=lambda x: x.get("date") or "")


def run_compliance_workflow(controls: list[dict[str, Any]], evidence: list[dict[str, Any]]) -> dict[str, Any]:
    mapping = map_evidence_to_controls(controls, evidence)
    return {
        "mapping": mapping,
        "coverage_score": coverage_score(mapping),
        "missing_evidence": missing_evidence_tasks(mapping),
        "reviewer_approval_required": True,
        "timeline": evidence_timeline(evidence),
        "status": "ready_for_review" if not missing_evidence_tasks(mapping) else "missing_evidence",
    }
