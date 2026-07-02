from app.core.audit import AuditLogger


def test_audit_logger_records_decisions():
    audit = AuditLogger()
    event = audit.record("user@example.com", "ai.decision", "run-1", reason="risk_score", score=82)
    assert event.action == "ai.decision"
    assert audit.as_dicts()[0]["details"]["score"] == 82
