from __future__ import annotations
from typing import Annotated
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.schemas import AuditLogOut
from app.core.deps import require_perm
from app.db.models import AuditLog, User
from app.db.session import get_db

router = APIRouter(prefix="/audit-logs", tags=["audit-logs"])

@router.get("", response_model=list[AuditLogOut])
def list_audit_logs(db: Annotated[Session, Depends(get_db)], user: Annotated[User, Depends(require_perm("audit:read"))]):
    return db.query(AuditLog).filter((AuditLog.organization_id == user.organization_id) | (AuditLog.organization_id.is_(None))).order_by(AuditLog.created_at.desc()).limit(200).all()
