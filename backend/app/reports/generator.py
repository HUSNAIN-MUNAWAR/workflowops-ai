from __future__ import annotations
from pathlib import Path
from typing import Any
import json, html


def _markdown(title: str, payload: dict[str, Any]) -> str:
    lines = [f"# {title}", "", "## Executive Summary", payload.get("executive_summary", "Synthetic demo report generated from local validation data."), ""]
    for section in ["input_files", "extracted_fields", "risk_score", "decisions_made", "approval_history", "audit_events", "recommendations", "limitations"]:
        value = payload.get(section, [])
        lines += [f"## {section.replace('_', ' ').title()}"]
        if isinstance(value, dict):
            for k, v in value.items(): lines.append(f"- **{k}**: {v}")
        elif isinstance(value, list):
            lines.extend([f"- {item}" for item in value] or ["- None recorded"])
        else:
            lines.append(str(value))
        lines.append("")
    return "\n".join(lines)


def _html(title: str, md: str) -> str:
    body = "\n".join(f"<p>{html.escape(line)}</p>" if not line.startswith('#') else f"<h{min(line.count('#'),3)}>{html.escape(line.strip('# '))}</h{min(line.count('#'),3)}>" for line in md.splitlines())
    return f"<!doctype html><html><head><meta charset='utf-8'><title>{html.escape(title)}</title><style>body{{font-family:Arial,sans-serif;max-width:960px;margin:40px auto;line-height:1.5}}h1,h2{{color:#172554}}p{{margin:6px 0}}</style></head><body>{body}</body></html>"


def _pdf(path: Path, title: str, md: str) -> None:
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet
        doc = SimpleDocTemplate(str(path), pagesize=A4)
        styles = getSampleStyleSheet()
        story = []
        for line in md.splitlines():
            if line.startswith('# '):
                story += [Paragraph(line[2:], styles['Title']), Spacer(1, 10)]
            elif line.startswith('## '):
                story += [Paragraph(line[3:], styles['Heading2']), Spacer(1, 6)]
            elif line.strip():
                story.append(Paragraph(html.escape(line), styles['BodyText']))
            else:
                story.append(Spacer(1, 6))
        doc.build(story)
    except Exception:
        path.write_text("PDF export unavailable in this environment. Markdown report is authoritative.", encoding="utf-8")


def generate_report(title: str, payload: dict[str, Any], output_dir: str | Path) -> dict[str, str]:
    out = Path(output_dir); out.mkdir(parents=True, exist_ok=True)
    slug = payload.get('slug') or title.lower().replace(' ', '_').replace('/', '_')
    json_path = out / f"{slug}.json"
    md_path = out / f"{slug}.md"
    html_path = out / f"{slug}.html"
    pdf_path = out / f"{slug}.pdf"
    md = _markdown(title, payload)
    json_path.write_text(json.dumps(payload, indent=2, default=str), encoding='utf-8')
    md_path.write_text(md, encoding='utf-8')
    html_path.write_text(_html(title, md), encoding='utf-8')
    _pdf(pdf_path, title, md)
    return {"json": str(json_path), "markdown": str(md_path), "html": str(html_path), "pdf": str(pdf_path)}

class ReportGenerator:
    def generate(self, title: str, payload: dict[str, Any], output_dir: str | Path = "sample_outputs/reports") -> dict[str, str]:
        return generate_report(title, payload, output_dir)


def generate_report_pack(title: str, payload: dict[str, Any], output_dir: str | Path, slug: str | None = None) -> dict[str, str]:
    data = dict(payload)
    if slug:
        data["slug"] = slug
    return generate_report(title, data, output_dir)


def build_report_payload(report_type: str, data: dict[str, Any]) -> dict[str, Any]:
    title_map={"invoice_approval":"Invoice Exception Report","rfp_response":"RFP Compliance Matrix","compliance_evidence":"Compliance Evidence Pack","support_escalation":"Customer Escalation Report","email_to_task":"Email-to-Task Operations Report"}
    return {"title":title_map.get(report_type,"Workflow Operations Report"),"slug":report_type+"_workflow_report","executive_summary":"Synthetic demo report generated from persisted workflow state.","input_files":data.get("input_files",["synthetic/demo input payload"]),"extracted_fields":data.get("extracted_fields",data.get("input",{})),"risk_score":data.get("risk_score",0),"decisions_made":["Persisted DAG steps executed","Policy decision recorded","Human approval required when threshold matched"],"approval_history":data.get("approval_history",["See approval_requests table for persisted decisions"]),"audit_events":data.get("audit_events",["workflow_started","workflow_node_completed","report_generated"]),"recommendations":["Review synthetic output before mapping to real client systems","Enable real connector security review before production use"],"limitations":["Synthetic demo/business-rule output","Not certified accounting/legal/compliance software"]}
