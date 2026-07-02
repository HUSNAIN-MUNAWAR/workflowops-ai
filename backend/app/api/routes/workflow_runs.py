
from __future__ import annotations
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.api.schemas import QueueJobOut, ReplayRequest, WorkflowRunCreate, WorkflowRunOut, WorkflowTimelineStep
from app.core.deps import require_perm, write_audit
from app.core.metrics import metrics
from app.db.models import User, WorkflowRun, WorkflowStepRun, WorkflowTemplate
from app.db.session import get_db
from app.queueing import enqueue_workflow_run
from app.workflows.dag import PersistedDAGScheduler
router=APIRouter(prefix="/workflow-runs",tags=["workflow-runs"])
@router.post("",response_model=WorkflowRunOut)
def create_run(payload:WorkflowRunCreate,request:Request,db:Annotated[Session,Depends(get_db)],user:Annotated[User,Depends(require_perm("workflow:run"))]):
    template=db.query(WorkflowTemplate).filter_by(organization_id=user.organization_id,slug=payload.template_slug).first()
    if not template: raise HTTPException(404,"Workflow template not found")
    try:
        sched=PersistedDAGScheduler(db,user.organization_id,user.email,user.role); run=sched.create_run(template,payload.input_payload,simulation_mode=payload.simulation_mode,idempotency_key=payload.idempotency_key); run=sched.run_until_blocked(run)
    except PermissionError as exc: raise HTTPException(403,str(exc))
    metrics.inc("workflow_runs_total"); write_audit(db,action="workflow_started",actor=user,target_type="workflow_run",target_id=run.id,request_id=getattr(request.state,"request_id",None),details={"template_slug":payload.template_slug}); return run
@router.post("/{run_id}/enqueue",response_model=QueueJobOut)
def enqueue(run_id:str,db:Annotated[Session,Depends(get_db)],user:Annotated[User,Depends(require_perm("workflow:enqueue"))]): return enqueue_workflow_run(db,_get_run(db,user,run_id))
@router.post("/{run_id}/resume",response_model=WorkflowRunOut)
def resume(run_id:str,request:Request,db:Annotated[Session,Depends(get_db)],user:Annotated[User,Depends(require_perm("workflow:resume"))]):
    run=PersistedDAGScheduler(db,user.organization_id,user.email,user.role).run_until_blocked(_get_run(db,user,run_id)); write_audit(db,action="workflow_resumed",actor=user,target_type="workflow_run",target_id=run.id,request_id=getattr(request.state,"request_id",None)); return run
@router.get("",response_model=list[WorkflowRunOut])
def list_runs(db:Annotated[Session,Depends(get_db)],user:Annotated[User,Depends(require_perm("workflow:read"))]): return db.query(WorkflowRun).filter_by(organization_id=user.organization_id).order_by(WorkflowRun.started_at.desc()).limit(100).all()
@router.get("/{run_id}",response_model=WorkflowRunOut)
def get_run(run_id:str,db:Annotated[Session,Depends(get_db)],user:Annotated[User,Depends(require_perm("workflow:read"))]): return _get_run(db,user,run_id)
@router.post("/{run_id}/cancel",response_model=WorkflowRunOut)
def cancel_run(run_id:str,request:Request,db:Annotated[Session,Depends(get_db)],user:Annotated[User,Depends(require_perm("workflow:stop"))]):
    row=PersistedDAGScheduler(db,user.organization_id,user.email,user.role).cancel(_get_run(db,user,run_id),"Cancelled by user kill switch"); write_audit(db,action="workflow_cancelled",actor=user,target_type="workflow_run",target_id=row.id,request_id=getattr(request.state,"request_id",None)); return row
@router.post("/{run_id}/replay",response_model=WorkflowRunOut)
def replay_run(run_id:str,request:Request,db:Annotated[Session,Depends(get_db)],user:Annotated[User,Depends(require_perm("workflow:replay"))],payload:ReplayRequest|None=None):
    row=PersistedDAGScheduler(db,user.organization_id,user.email,user.role).replay(_get_run(db,user,run_id),from_node_id=(payload.from_node_id if payload else None)); write_audit(db,action="workflow_replayed",actor=user,target_type="workflow_run",target_id=row.id,request_id=getattr(request.state,"request_id",None),details={"from_run_id":run_id}); return row
@router.get("/{run_id}/timeline",response_model=list[WorkflowTimelineStep])
def timeline(run_id:str,db:Annotated[Session,Depends(get_db)],user:Annotated[User,Depends(require_perm("workflow:read"))]):
    run=_get_run(db,user,run_id); return db.query(WorkflowStepRun).filter_by(workflow_run_id=run.id).order_by(WorkflowStepRun.created_at).all()
def _get_run(db:Session,user:User,run_id:str)->WorkflowRun:
    row=db.query(WorkflowRun).filter_by(organization_id=user.organization_id,id=run_id).first()
    if not row: raise HTTPException(404,"Workflow run not found")
    return row
