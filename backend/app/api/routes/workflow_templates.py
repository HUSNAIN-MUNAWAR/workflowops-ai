from __future__ import annotations
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.schemas import WorkflowTemplateOut
from app.core.deps import require_perm
from app.db.models import User, WorkflowTemplate
from app.db.session import get_db

router = APIRouter(prefix="/workflow-templates", tags=["workflow-templates"])

@router.get("", response_model=list[WorkflowTemplateOut])
def list_templates(db: Annotated[Session, Depends(get_db)], user: Annotated[User, Depends(require_perm("workflow:read"))]):
    return db.query(WorkflowTemplate).filter_by(organization_id=user.organization_id, is_active=True).order_by(WorkflowTemplate.name).all()

@router.get("/{template_id}", response_model=WorkflowTemplateOut)
def get_template(template_id: str, db: Annotated[Session, Depends(get_db)], user: Annotated[User, Depends(require_perm("workflow:read"))]):
    q = db.query(WorkflowTemplate).filter(WorkflowTemplate.organization_id == user.organization_id)
    row = q.filter((WorkflowTemplate.id == template_id) | (WorkflowTemplate.slug == template_id)).first()
    if not row:
        raise HTTPException(404, "Workflow template not found")
    return row
