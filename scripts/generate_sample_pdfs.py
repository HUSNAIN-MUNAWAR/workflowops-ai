from __future__ import annotations
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
ROOT = Path(__file__).resolve().parents[1]
PDF_DIR = ROOT / 'demo_data' / 'generated_pdfs'
PDF_DIR.mkdir(parents=True, exist_ok=True)

def make_pdf(name: str, title: str, lines: list[str]) -> str:
    path = PDF_DIR / name
    doc = SimpleDocTemplate(str(path), pagesize=A4)
    styles = getSampleStyleSheet()
    story = [Paragraph(title, styles['Title']), Spacer(1, 12)]
    for line in lines:
        story += [Paragraph(line, styles['BodyText']), Spacer(1, 6)]
    doc.build(story)
    return str(path)

def main():
    outputs = [
        make_pdf('synthetic_invoice_INV-2001.pdf','Synthetic Invoice INV-2001',['Vendor: Acme Supplies Ltd','Invoice Number: INV-2001','PO Number: PO-9001','Tax: USD 120.00','Total: USD 1250.00','Due Date: 2026-08-15','Demo note: synthetic data for WorkflowOps AI.']),
        make_pdf('synthetic_po_PO-9001.pdf','Synthetic Purchase Order PO-9001',['Supplier: Acme Supplies Ltd','PO Number: PO-9001','Total: USD 1250.00','Buyer: WorkflowOps Demo Organization']),
        make_pdf('synthetic_rfp_automation.pdf','Synthetic RFP - Automation Platform',['RFP: Request for Proposal','Deadline: 2026-09-01','Mandatory: Company profile document','Mandatory: ISO 27001-style security policy or equivalent statement','Required: Implementation plan and support SLA','Must provide pricing breakdown and compliance matrix.']),
        make_pdf('synthetic_support_attachment.pdf','Synthetic Support Attachment',['Ticket: T-100','Customer: VIP customer','Issue: urgent outage and refund request','Risk terms: legal escalation if not resolved.']),
        make_pdf('synthetic_policy_document.pdf','Synthetic Policy Document',['Policy: Access Control','Control ID: ISO-12.1','Evidence: Pull request approval and CI log retained for review.']),
    ]
    print('\n'.join(outputs))
if __name__ == '__main__': main()
