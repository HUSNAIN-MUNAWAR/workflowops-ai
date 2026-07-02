from __future__ import annotations
import subprocess, sys
from pathlib import Path
from _validation_utils import save_validation
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'backend'))
from app.documents.processor import process_document

def main():
    subprocess.check_call([sys.executable, str(ROOT/'scripts/generate_sample_pdfs.py')])
    invoice = process_document(ROOT/'demo_data/generated_pdfs/synthetic_invoice_INV-2001.pdf')
    rfp = process_document(ROOT/'demo_data/generated_pdfs/synthetic_rfp_automation.pdf')
    required = ['invoice_number','vendor','total','due_date']
    missing = [x for x in required if not invoice.fields.get(x)]
    if missing: raise SystemExit(f'Missing invoice fields: {missing}; got {invoice.fields}')
    if invoice.fields.get("invoice_number") != "INV-2001": raise SystemExit(f"Wrong invoice number: {invoice.fields.get('invoice_number')}")
    if not rfp.fields.get('mandatory_requirements'): raise SystemExit('Missing RFP mandatory requirements')
    save_validation('document_extraction_validation', {'status':'passed','invoice_fields':invoice.fields,'invoice_confidence':invoice.extraction_confidence,'rfp_requirements':rfp.fields.get('mandatory_requirements'),'warnings':invoice.warnings+rfp.warnings,'checks':['generated PDFs','extracted invoice number/vendor/amount/due date','extracted RFP mandatory requirements']})
if __name__=='__main__': main()
