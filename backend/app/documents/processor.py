from __future__ import annotations
from pathlib import Path
from dataclasses import dataclass
from app.core.security import detect_prompt_injection
from app.documents.classifier import classify_document
from app.documents.extraction import extract_for_document_type
from app.documents.parser import parse_document_path

@dataclass
class ProcessedDocument:
    filename: str
    content_type: str
    text: str
    document_type: str
    classification_confidence: float
    extraction_confidence: float
    fields: dict
    warnings: list[str]
    prompt_injection_findings: list[str]


def process_document(path: str | Path, content_type: str | None = None) -> ProcessedDocument:
    parsed = parse_document_path(path, content_type)
    classification = classify_document(parsed.text)
    extracted = extract_for_document_type(parsed.text, classification.document_type)
    findings = detect_prompt_injection(parsed.text)
    return ProcessedDocument(
        filename=parsed.filename,
        content_type=parsed.content_type,
        text=parsed.text,
        document_type=classification.document_type,
        classification_confidence=classification.confidence,
        extraction_confidence=extracted.confidence,
        fields=extracted.fields,
        warnings=parsed.warnings + extracted.warnings,
        prompt_injection_findings=findings,
    )
