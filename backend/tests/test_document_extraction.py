from app.documents.classifier import classify_document
from app.documents.extraction import extract_key_values, confidence_score


def test_invoice_classification_and_extraction():
    text = "Invoice Number: INV-22\nVendor: Acme\nTotal: USD 300\nDue Date: 2026-08-01"
    c = classify_document(text)
    fields = extract_key_values(text)
    assert c.document_type == "invoice"
    assert fields["invoice_number"] == "INV-22"
    assert confidence_score(fields, ["invoice_number", "vendor", "total", "due_date"]) == 1.0
