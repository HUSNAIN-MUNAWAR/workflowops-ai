from app.modules.invoice.service import invoice_risk_score


def test_invoice_risk_scores_duplicate_high():
    invoice = {"amount": 6000, "missing_fields": []}
    po = {"vendor_match": True, "amount_match": True}
    risk = invoice_risk_score(invoice, duplicate=True, po_match=po)
    assert risk["score"] >= 60
    assert "duplicate invoice detected" in risk["reasons"]
