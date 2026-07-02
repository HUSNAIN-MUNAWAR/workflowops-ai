from __future__ import annotations
from pathlib import Path
from dataclasses import dataclass, field
from typing import BinaryIO
import mimetypes

@dataclass
class ParsedDocument:
    filename: str
    content_type: str
    text: str
    warnings: list[str] = field(default_factory=list)

SUPPORTED_TEXT = {".txt", ".md", ".csv", ".json"}
SUPPORTED_PDF = {".pdf"}
SUPPORTED_IMAGE = {".png", ".jpg", ".jpeg", ".tif", ".tiff"}


def _read_pdf(path: Path) -> tuple[str, list[str]]:
    warnings: list[str] = []
    try:
        from pypdf import PdfReader
        reader = PdfReader(str(path))
        pages = [(p.extract_text() or "") for p in reader.pages]
        text = "\n".join(pages).strip()
        if not text:
            warnings.append("PDF text layer was empty; OCR fallback may be required.")
        return text, warnings
    except Exception as exc:
        return "", [f"PDF parsing failed: {exc}"]


def parse_document_path(path: str | Path, content_type: str | None = None) -> ParsedDocument:
    p = Path(path)
    ext = p.suffix.lower()
    ctype = content_type or mimetypes.guess_type(p.name)[0] or "application/octet-stream"
    if not p.exists():
        return ParsedDocument(p.name, ctype, "", ["File does not exist"])
    try:
        if ext in SUPPORTED_TEXT:
            return ParsedDocument(p.name, ctype, p.read_text(encoding="utf-8", errors="ignore"), [])
        if ext in SUPPORTED_PDF:
            text, warnings = _read_pdf(p)
            return ParsedDocument(p.name, ctype, text, warnings)
        if ext in SUPPORTED_IMAGE:
            from app.documents.ocr import ocr_image
            text, warnings = ocr_image(p)
            return ParsedDocument(p.name, ctype, text, warnings)
        return ParsedDocument(p.name, ctype, "", [f"Unsupported file type: {ext or 'unknown'}"])
    except Exception as exc:
        return ParsedDocument(p.name, ctype, "", [f"Malformed or unreadable file: {exc}"])


def parse_upload_file(file: BinaryIO, filename: str, dest: Path, content_type: str | None = None) -> ParsedDocument:
    dest.parent.mkdir(parents=True, exist_ok=True)
    data = file.read()
    dest.write_bytes(data)
    return parse_document_path(dest, content_type)
