from __future__ import annotations
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.api.schemas import TemplateValidateRequest, TemplateValidationOut, TemplateWriteRequest, WorkflowTemplateOut
from app.core.deps import require_perm, write_audit
from app.db.models import User, WorkflowTemplate
from app.db.session import get_db
from app.workflows.dag import validate_dag
router=APIRouter(prefix="/workflow-builder",tags=["workflow-builder"])
@router.post("/validate",response_model=TemplateValidationOut)
def validate(payload:TemplateValidateRequest,user:Annotated[User,Depends(require_perm("workflow:read"))]):
    errors=validate_dag(payload.definition_json); return {"valid":not errors,"errors":errors}
@router.post("/templates/{template_id}/clone",response_model=WorkflowTemplateOut)
def clone(template_id:str,request:Request,db:Annotated[Session,Depends(get_db)],user:Annotated[User,Depends(require_perm("template:write"))]):
    row=db.query(WorkflowTemplate).filter_by(organization_id=user.organization_id,id=template_id).first()
    if not row: raise HTTPException(404,"Template not found")
    slug=row.slug+"_clone"; i=1
    while db.query(WorkflowTemplate).filter_by(organization_id=user.organization_id,slug=slug).first(): i+=1; slug=f"{row.slug}_clone_{i}"
    clone=WorkflowTemplate(organization_id=user.organization_id,slug=slug,name=row.name+" Clone",description=row.description,version="1.0.0-draft",risk_threshold=row.risk_threshold,definition_json=row.definition_json,is_active=False); db.add(clone); db.commit(); db.refresh(clone); write_audit(db,action="template.cloned",actor=user,target_type="workflow_template",target_id=clone.id,request_id=getattr(request.state,"request_id",None),details={"source_template_id":template_id}); return clone
@router.post("/templates",response_model=WorkflowTemplateOut)
def save_template(payload:TemplateWriteRequest,request:Request,db:Annotated[Session,Depends(get_db)],user:Annotated[User,Depends(require_perm("template:write"))]):
    errors=validate_dag(payload.definition_json)
    if errors: raise HTTPException(422,{"errors":errors})
    if db.query(WorkflowTemplate).filter_by(organization_id=user.organization_id,slug=payload.slug).first(): raise HTTPException(409,"Template slug already exists")
    row=WorkflowTemplate(organization_id=user.organization_id,slug=payload.slug,name=payload.name,description=payload.description,version=payload.version,risk_threshold=payload.risk_threshold,definition_json=payload.definition_json,is_active=payload.is_active); db.add(row); db.commit(); db.refresh(row); write_audit(db,action="template.saved",actor=user,target_type="workflow_template",target_id=row.id,request_id=getattr(request.state,"request_id",None)); return row
@router.post("/templates/{template_id}/publish",response_model=WorkflowTemplateOut)
def publish(template_id:str,request:Request,db:Annotated[Session,Depends(get_db)],user:Annotated[User,Depends(require_perm("template:write"))]):
    row=db.query(WorkflowTemplate).filter_by(organization_id=user.organization_id,id=template_id).first()
    if not row: raise HTTPException(404,"Template not found")
    errors=validate_dag(row.definition_json)
    if errors: raise HTTPException(422,{"errors":errors})
    row.is_active=True; db.commit(); db.refresh(row); write_audit(db,action="template.published",actor=user,target_type="workflow_template",target_id=row.id,request_id=getattr(request.state,"request_id",None)); return row
