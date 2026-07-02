from app.workflows.approvals import ApprovalRequest, decide_approval, should_request_approval


def test_approval_required_for_sensitive_action():
    assert should_request_approval(20, 65, "payment_export") is True


def test_approval_decision():
    req = ApprovalRequest("Approve payment", "demo", 80)
    decided = decide_approval(req, "approved", "Synthetic invoice reviewed")
    assert decided.status == "approved"
