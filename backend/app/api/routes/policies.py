
from __future__ import annotations
from typing import Annotated
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from app.api.schemas import PolicyDecisionOut, PolicyEvaluateRequest, PolicyOut, PolicyUpdate
from app.core.deps import require_perm, write_audit
from app.db.models import User
from app.db.session import get_db
from app.policies.engine import ensure_default_policy, evaluate_policy, update_policy
router=APIRouter(prefix="/policies",tags=["policies"])
@router.get("",response_model=list[PolicyOut])
def list_policies(db:Annotated[Session,Depends(get_db)],user:Annotated[User,Depends(require_perm("policy:read"))]): return [ensure_default_policy(db,user.organization_id)]
@router.get("/default",response_model=PolicyOut)
def get_default(db:Annotated[Session,Depends(get_db)],user:Annotated[User,Depends(require_perm("policy:read"))]): return ensure_default_policy(db,user.organization_id)
@router.put("/default",response_model=PolicyOut)
def put_default(payload:PolicyUpdate,request:Request,db:Annotated[Session,Depends(get_db)],user:Annotated[User,Depends(require_perm("policy:write"))]):
    vals={k:v for k,v in payload.model_dump().items() if v is not None}; row=update_policy(db,user.organization_id,vals); write_audit(db,action="policy.updated",actor=user,target_type="policy",target_id=row.id,request_id=getattr(request.state,"request_id",None),details={"updated_fields":list(vals)}); return row
@router.post("/evaluate",response_model=PolicyDecisionOut)
def evaluate(payload:PolicyEvaluateRequest,db:Annotated[Session,Depends(get_db)],user:Annotated[User,Depends(require_perm("policy:read"))]): return evaluate_policy(db,user.organization_id,actor=user,action=payload.action,payload=payload.payload).dict()
