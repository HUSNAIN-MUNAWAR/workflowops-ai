
from __future__ import annotations
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.api.schemas import ConnectorActionOut, ConnectorActionRequest, ConnectorOut
from app.connectors.registry import get_connector, list_connectors
from app.core.deps import require_perm, write_audit
from app.db.models import ConnectorActionLog, User
from app.db.session import get_db
from app.policies.engine import evaluate_policy
router=APIRouter(prefix="/connectors",tags=["connectors"])
def _out(c): return {"connector_id":c.connector_id,"name":c.name,"category":c.category,"description":c.description,"actions":[a.__dict__ for a in c.list_actions()]}
@router.get("",response_model=list[ConnectorOut])
def connectors(user:Annotated[User,Depends(require_perm("connector:read"))]): return [_out(c) for c in list_connectors()]
@router.get("/{connector_id}",response_model=ConnectorOut)
def connector(connector_id:str,user:Annotated[User,Depends(require_perm("connector:read"))]):
    try: return _out(get_connector(connector_id))
    except KeyError: raise HTTPException(404,"Connector not found")
@router.post("/{connector_id}/test",response_model=ConnectorActionOut)
def test_connector(connector_id:str,request:Request,db:Annotated[Session,Depends(get_db)],user:Annotated[User,Depends(require_perm("connector:test"))]): return _run(connector_id,"test",{"payload":{"ping":True}},True,request,db,user)
@router.post("/{connector_id}/actions/{action_name}/dry-run",response_model=ConnectorActionOut)
def dry_run(connector_id:str,action_name:str,payload:ConnectorActionRequest,request:Request,db:Annotated[Session,Depends(get_db)],user:Annotated[User,Depends(require_perm("connector:dry_run"))]): return _run(connector_id,action_name,payload.model_dump(),True,request,db,user)
@router.post("/{connector_id}/actions/{action_name}/execute",response_model=ConnectorActionOut)
def execute(connector_id:str,action_name:str,payload:ConnectorActionRequest,request:Request,db:Annotated[Session,Depends(get_db)],user:Annotated[User,Depends(require_perm("connector:execute"))]): return _run(connector_id,action_name,payload.model_dump(),False,request,db,user)
def _run(connector_id,action_name,payload_wrapper,dry,request,db,user):
    try: conn=get_connector(connector_id)
    except KeyError: raise HTTPException(404,"Connector not found")
    if action_name=="test": action_name=next(iter(conn.actions)) if conn.actions else "test"
    payload=payload_wrapper.get("payload",payload_wrapper); action=conn.actions.get(action_name)
    if not action: raise HTTPException(400,"Unsupported connector action")
    decision=evaluate_policy(db,user.organization_id,actor=user,action="connector_execute",payload={"connector_id":connector_id,"high_risk":action.high_risk})
    if not decision.allowed:
        db.add(ConnectorActionLog(organization_id=user.organization_id,connector_id=connector_id,action_name=action_name,mode="dry_run" if dry else "execute",status="blocked",request_payload=payload,response_payload=decision.dict())); db.commit(); write_audit(db,action="connector_blocked",actor=user,target_type="connector",target_id=connector_id,outcome="blocked",request_id=getattr(request.state,"request_id",None),details=decision.dict()); raise HTTPException(403,decision.reason)
    if not dry and decision.requires_approval:
        db.add(ConnectorActionLog(organization_id=user.organization_id,connector_id=connector_id,action_name=action_name,mode="execute",status="approval_required",request_payload=payload,response_payload=decision.dict())); db.commit(); write_audit(db,action="connector_blocked",actor=user,target_type="connector",target_id=connector_id,outcome="approval_required",request_id=getattr(request.state,"request_id",None),details=decision.dict()); raise HTTPException(409,"High-risk connector execution requires workflow approval in demo mode.")
    result=conn.execute(db,user.organization_id,action_name,payload,dry_run=dry); db.add(ConnectorActionLog(organization_id=user.organization_id,connector_id=connector_id,action_name=action_name,mode="dry_run" if dry else "execute",status=result.status,idempotency_key=payload_wrapper.get("idempotency_key"),request_payload=payload,response_payload=result.data)); db.commit(); write_audit(db,action="connector_dry_run" if dry else "connector_executed",actor=user,target_type="connector",target_id=connector_id,request_id=getattr(request.state,"request_id",None),details={"action":action_name,"status":result.status}); return result.__dict__
