from __future__ import annotations
from typing import Annotated, Callable
from fastapi import Depends, Header, HTTPException, Request, status
from sqlalchemy.orm import Session
from app.core.config import get_settings
from app.core.rbac import has_permission
from app.core.security import verify_access_token
from app.db.models import AuditLog, User
from app.db.session import get_db

def write_audit(db: Session, *, action: str, actor: User | None = None, organization_id: str | None = None, target_type: str = "system", target_id: str | None = None, outcome: str = "success", request_id: str | None = None, details: dict | None = None):
    row = AuditLog(organization_id=organization_id or (actor.organization_id if actor else None), actor_email=actor.email if actor else "anonymous", actor_role=actor.role if actor else "anonymous", action=action, target_type=target_type, target_id=target_id, outcome=outcome, request_id=request_id, details=details or {})
    db.add(row); db.commit(); db.refresh(row); return row

def get_current_user(db: Annotated[Session, Depends(get_db)], request: Request, authorization: Annotated[str | None, Header()] = None) -> User:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")
    try:
        payload = verify_access_token(authorization.split(" ", 1)[1], get_settings().jwt_secret)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user = db.query(User).filter(User.email == payload["sub"], User.is_active.is_(True)).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    request.state.current_user = user
    return user

def require_perm(permission: str) -> Callable:
    def _dep(request: Request, db: Annotated[Session, Depends(get_db)], user: Annotated[User, Depends(get_current_user)]) -> User:
        if not has_permission(user.role, permission):
            write_audit(db, action=f"denied.{permission}", actor=user, outcome="denied", request_id=getattr(request.state, "request_id", None), details={"permission": permission})
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Permission denied: {permission}")
        return user
    return _dep
