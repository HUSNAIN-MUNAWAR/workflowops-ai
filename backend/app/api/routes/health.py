from __future__ import annotations
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.models import AuditLog, ApprovalRequest, ConnectorActionLog, Document, QueueJob, ReliabilityTestRun, Report, WorkflowRun
from app.db.session import get_db
router=APIRouter(tags=["ops"])
@router.get("/health")
def health(): return {"status":"ok"}
@router.get("/ready")
def ready(db:Session=Depends(get_db)): return {"status":"ready"}
@router.get("/queue/status")
def queue_status_compat(db:Session=Depends(get_db)):
    from app.queueing import queue_status
    return queue_status(db)
@router.get("/metrics")
def metrics(db:Session=Depends(get_db)):
    vals={"workflow_runs_total":db.query(WorkflowRun).count(),"workflow_runs_failed_total":db.query(WorkflowRun).filter(WorkflowRun.status.like("%fail%")).count(),"workflow_runs_queued_total":db.query(WorkflowRun).filter_by(status="queued").count(),"pending_approvals_total":db.query(ApprovalRequest).filter_by(status="pending").count(),"documents_processed_total":db.query(Document).count(),"reliability_tests_total":db.query(ReliabilityTestRun).count(),"audit_logs_total":db.query(AuditLog).count(),"queue_jobs_failed_total":db.query(QueueJob).filter_by(status="failed").count(),"connector_actions_total":db.query(ConnectorActionLog).count(),"reports_total":db.query(Report).count()}
    return "\n".join([f"# TYPE {k} counter\n{k} {v}" for k,v in vals.items()])+"\n"
