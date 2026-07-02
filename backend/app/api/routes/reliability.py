from __future__ import annotations
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.api.schemas import ReliabilityRunCreate, ReliabilityRunOut
from app.core.deps import require_perm, write_audit
from app.core.metrics import metrics
from app.db.models import ReliabilityTestCaseResult, ReliabilityTestRun, User
from app.db.session import get_db
from app.modules.reliability.evalbench import run_reliability_suite
from app.reports.generator import generate_report

router = APIRouter(prefix="/reliability-tests", tags=["reliability-tests"])

@router.post("/run", response_model=ReliabilityRunOut)
def run_reliability(payload: ReliabilityRunCreate, request: Request, db: Annotated[Session, Depends(get_db)], user: Annotated[User, Depends(require_perm("reliability:run"))]):
    result = run_reliability_suite(payload.template_slug)
    paths = generate_report("Workflow Reliability Test Report", {"slug":"workflow_reliability_test_report", "executive_summary": result["demo_note"], "risk_score": result["reliability_score"], "decisions_made": [f"{c['test_name']}: {'passed' if c['passed'] else 'failed'}" for c in result['cases']], "recommendations": [c['mitigation_recommendation'] for c in result['failed_cases']] or ["No failed cases in this synthetic run"], "limitations": ["Synthetic deterministic reliability evaluation, not a formal benchmark"]}, "sample_outputs/reports")
    row = ReliabilityTestRun(organization_id=user.organization_id, workflow_template_slug=payload.template_slug, status="completed", reliability_score=result["reliability_score"], safety_score=result["safety_score"], failed_cases=result["failed_count"], report_paths=paths, replay_logs=result["replay_logs"])
    db.add(row); db.commit(); db.refresh(row)
    for case in result["cases"]:
        db.add(ReliabilityTestCaseResult(reliability_test_run_id=row.id, test_name=case["test_name"], scenario_type=case["scenario_type"], input_mutation=case["input_mutation"], expected_behavior=case["expected_behavior"], actual_behavior=case["actual_behavior"], passed=case["passed"], severity=case["severity"], evidence={"items": case["evidence"]}, mitigation_recommendation=case["mitigation_recommendation"]))
    db.commit(); db.refresh(row)
    metrics.inc("reliability_tests_total")
    write_audit(db, action="reliability.run.completed", actor=user, target_type="reliability_test_run", target_id=row.id, request_id=getattr(request.state,"request_id",None), details={"failed_cases": result["failed_count"]})
    return row

@router.get("", response_model=list[ReliabilityRunOut])
def list_runs(db: Annotated[Session, Depends(get_db)], user: Annotated[User, Depends(require_perm("reliability:read"))]):
    return db.query(ReliabilityTestRun).filter_by(organization_id=user.organization_id).order_by(ReliabilityTestRun.created_at.desc()).all()

@router.get("/{test_run_id}")
def get_run(test_run_id: str, db: Annotated[Session, Depends(get_db)], user: Annotated[User, Depends(require_perm("reliability:read"))]):
    row = db.query(ReliabilityTestRun).filter_by(organization_id=user.organization_id, id=test_run_id).first()
    if not row: raise HTTPException(404, "Reliability run not found")
    cases = db.query(ReliabilityTestCaseResult).filter_by(reliability_test_run_id=row.id).all()
    return {"run": row, "cases": cases}

@router.get("/{test_run_id}/report")
def get_report(test_run_id: str, db: Annotated[Session, Depends(get_db)], user: Annotated[User, Depends(require_perm("reliability:read"))]):
    row = db.query(ReliabilityTestRun).filter_by(organization_id=user.organization_id, id=test_run_id).first()
    if not row: raise HTTPException(404, "Reliability run not found")
    return {"report_paths": row.report_paths, "replay_logs": row.replay_logs, "summary": {"reliability_score": row.reliability_score, "safety_score": row.safety_score, "failed_cases": row.failed_cases}}
