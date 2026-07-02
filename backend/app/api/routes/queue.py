from __future__ import annotations
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.deps import require_perm, write_audit
from app.db.models import QueueJob, User
from app.db.session import get_db
from app.queueing import queue_status, retry_failed_job
router=APIRouter(prefix="/queue",tags=["queue"])
@router.get("/status")
def status(db:Annotated[Session,Depends(get_db)],user:Annotated[User,Depends(require_perm("queue:read"))]): return queue_status(db)
@router.get("/failed-jobs")
def failed_jobs(db:Annotated[Session,Depends(get_db)],user:Annotated[User,Depends(require_perm("queue:read"))]): return [{"id":r.id,"workflow_run_id":r.workflow_run_id,"node_id":r.node_id,"attempts":r.attempts,"last_error":r.last_error,"created_at":r.created_at} for r in db.query(QueueJob).filter_by(status="failed").order_by(QueueJob.created_at.desc()).limit(100).all()]
@router.post("/failed-jobs/{job_id}/retry")
def retry(job_id:str,db:Annotated[Session,Depends(get_db)],user:Annotated[User,Depends(require_perm("queue:retry"))]):
    try: row=retry_failed_job(db,job_id)
    except ValueError as exc: raise HTTPException(400,str(exc))
    write_audit(db,action="queue_job_retried",actor=user,target_type="queue_job",target_id=row.id,details={"status":row.status}); return {"id":row.id,"status":row.status,"attempts":row.attempts}
