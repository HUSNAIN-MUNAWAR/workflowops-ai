
from __future__ import annotations
from datetime import datetime, timezone
from typing import Any
from sqlalchemy.orm import Session
from app.core.config import get_settings
from app.db.session import SessionLocal
from app.db.models import QueueJob, WorkflowRun
def enqueue_workflow_run(db:Session,run:WorkflowRun,node_id:str|None=None)->QueueJob:
    job=QueueJob(organization_id=run.organization_id,workflow_run_id=run.id,node_id=node_id,status="queued",heartbeat_at=datetime.now(timezone.utc)); db.add(job); run.status="queued"; db.commit(); db.refresh(job); db.refresh(run)
    settings=get_settings()
    if settings.local_sync_worker: execute_job_sync(db,job.id)
    else:
        try:
            from redis import Redis
            from rq import Queue
            q=Queue("workflowops",connection=Redis.from_url(settings.redis_url)); rq_job=q.enqueue("app.queueing.execute_job_by_id",job.id,job_timeout=300); job.rq_job_id=rq_job.id; db.commit(); db.refresh(job)
        except Exception as exc: job.status="failed"; job.last_error=f"RQ enqueue failed: {exc}"; db.commit(); db.refresh(job)
    return job
def execute_job_by_id(job_id:str)->str:
    db=SessionLocal()
    try: return execute_job_sync(db,job_id).status
    finally: db.close()
def execute_job_sync(db:Session,job_id:str)->QueueJob:
    from app.workflows.dag import PersistedDAGScheduler
    job=db.query(QueueJob).filter_by(id=job_id).first()
    if not job: raise ValueError("Job not found")
    run=db.query(WorkflowRun).filter_by(id=job.workflow_run_id).first()
    if not run: job.status="failed"; job.last_error="Workflow run not found"; db.commit(); return job
    if run.status=="cancelled": job.status="cancelled"; job.heartbeat_at=datetime.now(timezone.utc); db.commit(); db.refresh(job); return job
    job.status="running"; job.heartbeat_at=datetime.now(timezone.utc); job.attempts+=1; db.commit()
    try:
        sched=PersistedDAGScheduler(db,run.organization_id,"worker@local","system"); sched.run_until_blocked(run,replay_from=job.node_id); job.status="completed" if run.status in {"completed","waiting_for_approval","partially_completed"} else "failed" if run.status=="failed" else "completed"
    except Exception as exc: job.status="failed"; job.last_error=str(exc)
    job.heartbeat_at=datetime.now(timezone.utc); db.commit(); db.refresh(job); return job
def retry_failed_job(db:Session,job_id:str)->QueueJob:
    job=db.query(QueueJob).filter_by(id=job_id).first()
    if not job: raise ValueError("Job not found")
    if job.status!="failed": raise ValueError("Only failed jobs can be retried")
    job.status="queued"; job.last_error=None; db.commit(); db.refresh(job)
    if get_settings().local_sync_worker: return execute_job_sync(db,job.id)
    return job
def queue_status(db:Session)->dict[str,Any]:
    statuses=["queued","running","completed","failed","cancelled"]; counts={s:db.query(QueueJob).filter_by(status=s).count() for s in statuses}; latest=db.query(QueueJob).order_by(QueueJob.created_at.desc()).limit(5).all()
    return {"mode":"local_sync" if get_settings().local_sync_worker else "rq_redis","counts":counts,"worker_heartbeat":datetime.now(timezone.utc).isoformat(),"latest_jobs":[{"id":j.id,"run_id":j.workflow_run_id,"status":j.status,"attempts":j.attempts,"last_error":j.last_error,"rq_job_id":j.rq_job_id} for j in latest]}
