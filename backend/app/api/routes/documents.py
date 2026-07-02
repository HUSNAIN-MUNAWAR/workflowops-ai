from __future__ import annotations
from pathlib import Path
from typing import Annotated
from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile
from sqlalchemy.orm import Session
from app.api.schemas import DocumentOut, ExtractedFieldOut
from app.core.deps import require_perm, write_audit
from app.core.metrics import metrics
from app.db.models import Document, ExtractedField, User
from app.db.session import get_db
from app.documents.parser import parse_document_path
from app.documents.classifier import classify_document
from app.documents.extraction import extract_for_document_type
from app.core.security import detect_prompt_injection

router = APIRouter(prefix="/documents", tags=["documents"])
UPLOAD_DIR = Path("sample_outputs/uploads")
ALLOWED_SUFFIXES={".pdf",".txt",".csv",".md",".png",".jpg",".jpeg"}

@router.post("/upload", response_model=DocumentOut)
async def upload_document(request: Request, db: Annotated[Session, Depends(get_db)], user: Annotated[User, Depends(require_perm("document:upload"))], file: UploadFile = File(...)):
    safe_name = Path(file.filename or "uploaded_document.bin").name
    suffix = Path(safe_name).suffix.lower()
    if suffix not in ALLOWED_SUFFIXES:
        write_audit(db, action="access_denied", actor=user, target_type="document", request_id=getattr(request.state,"request_id",None), details={"reason":"unsupported_file_type", "filename": safe_name})
        raise HTTPException(400, "Unsupported file type for demo document processing")
    dest = UPLOAD_DIR / safe_name
    dest.parent.mkdir(parents=True, exist_ok=True)
    data = await file.read()
    if len(data) > 10 * 1024 * 1024:
        raise HTTPException(413, "File exceeds configured upload limit")
    dest.write_bytes(data)
    parsed = parse_document_path(dest, file.content_type)
    classification = classify_document(parsed.text)
    extraction = extract_for_document_type(parsed.text, classification.document_type)
    findings = detect_prompt_injection(parsed.text)
    row = Document(organization_id=user.organization_id, filename=safe_name, content_type=file.content_type or parsed.content_type, storage_path=str(dest), text_content=parsed.text, document_type=classification.document_type, classification_confidence=classification.confidence, extraction_confidence=extraction.confidence, warnings=parsed.warnings + extraction.warnings, prompt_injection_findings=findings)
    db.add(row); db.commit(); db.refresh(row)
    for name, value in extraction.fields.items():
        db.add(ExtractedField(document_id=row.id, name=name, value=value, confidence=extraction.confidence, source="demo_business_rule_extractor"))
    db.commit(); db.refresh(row)
    metrics.inc("documents_processed_total")
    write_audit(db, action="document.uploaded", actor=user, target_type="document", target_id=row.id, request_id=getattr(request.state,"request_id",None), details={"filename": safe_name, "synthetic_demo_extraction": True})
    return row

@router.get("", response_model=list[DocumentOut])
def list_documents(db: Annotated[Session, Depends(get_db)], user: Annotated[User, Depends(require_perm("document:read"))]):
    return db.query(Document).filter_by(organization_id=user.organization_id).order_by(Document.created_at.desc()).limit(100).all()

@router.get("/{document_id}", response_model=DocumentOut)
def get_document(document_id: str, db: Annotated[Session, Depends(get_db)], user: Annotated[User, Depends(require_perm("document:read"))]):
    row = db.query(Document).filter_by(organization_id=user.organization_id, id=document_id).first()
    if not row: raise HTTPException(404, "Document not found")
    return row

@router.get("/{document_id}/extracted-fields", response_model=list[ExtractedFieldOut])
def extracted_fields(document_id: str, db: Annotated[Session, Depends(get_db)], user: Annotated[User, Depends(require_perm("document:read"))]):
    row = db.query(Document).filter_by(organization_id=user.organization_id, id=document_id).first()
    if not row: raise HTTPException(404, "Document not found")
    return db.query(ExtractedField).filter_by(document_id=row.id).all()
