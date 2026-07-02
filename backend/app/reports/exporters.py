from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Any


def export_json(data: dict[str, Any], path: str | Path) -> Path:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")
    return p


def export_markdown(title: str, data: dict[str, Any], path: str | Path) -> Path:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    lines = [f"# {title}", "", "Generated from deterministic synthetic demo data.", ""]
    for key, value in data.items():
        lines.append(f"## {key.replace('_', ' ').title()}")
        if isinstance(value, (dict, list)):
            lines.append("```json")
            lines.append(json.dumps(value, indent=2, default=str))
            lines.append("```")
        else:
            lines.append(str(value))
        lines.append("")
    p.write_text("\n".join(lines), encoding="utf-8")
    return p


def export_html(title: str, data: dict[str, Any], path: str | Path) -> Path:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    body = html.escape(json.dumps(data, indent=2, default=str))
    p.write_text(f"<html><head><title>{html.escape(title)}</title></head><body><h1>{html.escape(title)}</h1><pre>{body}</pre></body></html>", encoding="utf-8")
    return p


def export_pdf(title: str, data: dict[str, Any], path: str | Path) -> Path | None:
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
    except Exception:
        return None
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(p), pagesize=letter)
    width, height = letter
    y = height - 40
    c.setFont("Helvetica-Bold", 14)
    c.drawString(40, y, title[:80])
    y -= 30
    c.setFont("Helvetica", 8)
    text = json.dumps(data, indent=2, default=str).splitlines()
    for line in text[:90]:
        if y < 40:
            c.showPage()
            c.setFont("Helvetica", 8)
            y = height - 40
        c.drawString(40, y, line[:120])
        y -= 10
    c.save()
    return p
