from __future__ import annotations
from pathlib import Path
from typing import Annotated, Literal
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.api.schemas import ReportOut
from app.core.deps import require_perm, write_audit
from app.db.models import Report, User
from app.db.session import get_db

router = APIRouter(prefix="/reports", tags=["reports"])

@router.get("", response_model=list[ReportOut])
def list_reports(db: Annotated[Session, Depends(get_db)], user: Annotated[User, Depends(require_perm("report:read"))]):
    return db.query(Report).filter_by(organization_id=user.organization_id).order_by(Report.created_at.desc()).all()

@router.get("/{report_id}", response_model=ReportOut)
def get_report(report_id: str, db: Annotated[Session, Depends(get_db)], user: Annotated[User, Depends(require_perm("report:read"))]):
    row = db.query(Report).filter_by(organization_id=user.organization_id, id=report_id).first()
    if not row: raise HTTPException(404, "Report not found")
    return row

@router.get("/{report_id}/download")
def download_report(report_id: str, request: Request, db: Annotated[Session, Depends(get_db)], user: Annotated[User, Depends(require_perm("report:export"))], format: Literal["json","md","html","pdf"] = Query("json")):
    row = db.query(Report).filter_by(organization_id=user.organization_id, id=report_id).first()
    if not row: raise HTTPException(404, "Report not found")
    key = "markdown" if format == "md" else format
    path = Path(row.paths.get(key, ""))
    if not path.exists():
        raise HTTPException(404, f"Report format not found: {format}")
    write_audit(db, action="report.downloaded", actor=user, target_type="report", target_id=row.id, request_id=getattr(request.state,"request_id",None), details={"format": format})
    return FileResponse(path, filename=path.name)
