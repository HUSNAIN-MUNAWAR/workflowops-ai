
from __future__ import annotations
from datetime import datetime, timezone
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.api.schemas import ApprovalDecision, ApprovalOut
from app.core.deps import require_perm, write_audit
from app.db.models import ApprovalRequest, User
from app.db.session import get_db
from app.workflows.dag import PersistedDAGScheduler
router=APIRouter(prefix="/approvals",tags=["approvals"])
@router.get("",response_model=list[ApprovalOut])
def list_approvals(db:Annotated[Session,Depends(get_db)],user:Annotated[User,Depends(require_perm("approval:read"))]): return db.query(ApprovalRequest).filter_by(organization_id=user.organization_id).order_by(ApprovalRequest.created_at.desc()).all()
@router.get("/{approval_id}",response_model=ApprovalOut)
def get_approval(approval_id:str,db:Annotated[Session,Depends(get_db)],user:Annotated[User,Depends(require_perm("approval:read"))]): return _get(db,user,approval_id)
@router.post("/{approval_id}/approve",response_model=ApprovalOut)
def approve(approval_id:str,payload:ApprovalDecision,request:Request,db:Annotated[Session,Depends(get_db)],user:Annotated[User,Depends(require_perm("approval:decide"))]): return _decide(db,user,request,approval_id,"approved",payload.reason)
@router.post("/{approval_id}/reject",response_model=ApprovalOut)
def reject(approval_id:str,payload:ApprovalDecision,request:Request,db:Annotated[Session,Depends(get_db)],user:Annotated[User,Depends(require_perm("approval:decide"))]): return _decide(db,user,request,approval_id,"rejected",payload.reason)
@router.post("/{approval_id}/request-changes",response_model=ApprovalOut)
def changes(approval_id:str,payload:ApprovalDecision,request:Request,db:Annotated[Session,Depends(get_db)],user:Annotated[User,Depends(require_perm("approval:decide"))]): return _decide(db,user,request,approval_id,"changes_requested",payload.reason)
def _get(db,user,approval_id):
    row=db.query(ApprovalRequest).filter_by(organization_id=user.organization_id,id=approval_id).first()
    if not row: raise HTTPException(404,"Approval not found")
    return row
def _decide(db,user,request,approval_id,status,reason):
    row=_get(db,user,approval_id); row.status=status; row.decision_by=user.email; row.decision_reason=reason; row.decided_at=datetime.now(timezone.utc); db.commit(); db.refresh(row); write_audit(db,action=f"approval_{status}",actor=user,target_type="approval",target_id=row.id,request_id=getattr(request.state,"request_id",None),details={"reason":reason})
    if status=="approved": PersistedDAGScheduler(db,user.organization_id,user.email,user.role).approve_and_resume(row,True,reason)
    elif status=="rejected": PersistedDAGScheduler(db,user.organization_id,user.email,user.role).approve_and_resume(row,False,reason)
    db.refresh(row); return row
