from __future__ import annotations
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from app.api.schemas import LoginRequest, TokenResponse, UserMe
from app.core.config import get_settings
from app.core.deps import get_current_user, write_audit
from app.core.security import create_access_token, verify_password
from app.db.models import User
from app.db.session import get_db

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, request: Request, db: Annotated[Session, Depends(get_db)]):
    user = db.query(User).filter(User.email == payload.email, User.is_active.is_(True)).first()
    if not user or not verify_password(payload.password, user.password_hash):
        write_audit(db, action="auth.login.failed", actor=None, outcome="denied", request_id=getattr(request.state, "request_id", None), details={"email": payload.email})
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    token = create_access_token(user.email, user.role, user.organization_id, get_settings().jwt_secret, get_settings().jwt_expire_minutes)
    write_audit(db, action="auth.login.success", actor=user, target_type="user", target_id=user.id, request_id=getattr(request.state, "request_id", None))
    return {"access_token": token, "user": {"id": user.id, "email": user.email, "full_name": user.full_name, "role": user.role, "organization_id": user.organization_id}}

@router.get("/me", response_model=UserMe)
def me(user: Annotated[User, Depends(get_current_user)]):
    return user
