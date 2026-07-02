from __future__ import annotations
from typing import Annotated
from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.api.schemas import DashboardSummary
from app.core.deps import require_perm
from app.db.models import ApprovalRequest, Document, ReliabilityTestRun, User, WorkflowRun
from app.db.session import get_db

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

@router.get("/summary", response_model=DashboardSummary)
def summary(db: Annotated[Session, Depends(get_db)], user: Annotated[User, Depends(require_perm("workflow:read"))]):
    org = user.organization_id
    total = db.query(WorkflowRun).filter_by(organization_id=org).count()
    failed = db.query(WorkflowRun).filter_by(organization_id=org, status="failed").count()
    pending = db.query(ApprovalRequest).filter_by(organization_id=org, status="pending").count()
    docs = db.query(Document).filter_by(organization_id=org).count()
    rel_scores = [r.reliability_score for r in db.query(ReliabilityTestRun).filter_by(organization_id=org).all()]
    rows = db.query(WorkflowRun.template_slug, func.count(WorkflowRun.id)).filter_by(organization_id=org).group_by(WorkflowRun.template_slug).all()
    return DashboardSummary(total_workflow_runs=total, pending_approvals=pending, failed_automations=failed, average_reliability_score=round(sum(rel_scores)/len(rel_scores),2) if rel_scores else 0, documents_processed=docs, sla_breaches=0, template_usage={k:v for k,v in rows})

@router.get("/recent-runs")
def recent_runs(db: Annotated[Session, Depends(get_db)], user: Annotated[User, Depends(require_perm("workflow:read"))]):
    return db.query(WorkflowRun).filter_by(organization_id=user.organization_id).order_by(WorkflowRun.started_at.desc()).limit(10).all()

@router.get("/risk-distribution")
def risk_distribution(db: Annotated[Session, Depends(get_db)], user: Annotated[User, Depends(require_perm("workflow:read"))]):
    runs = db.query(WorkflowRun).filter_by(organization_id=user.organization_id).all()
    out = {"low":0,"medium":0,"high":0}
    for r in runs:
        out["high" if r.risk_score >=70 else "medium" if r.risk_score>=40 else "low"] += 1
    return out
