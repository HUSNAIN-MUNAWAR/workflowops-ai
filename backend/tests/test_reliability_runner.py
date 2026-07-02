from app.modules.reliability.evalbench import run_reliability_suite


def test_reliability_suite_reports_intentional_demo_gaps():
    suite = run_reliability_suite()
    assert suite["suite"] == "workflow_evalbench"
    assert suite["total"] >= 12
    assert suite["reliability_score"] >= 80
    assert suite["failed_count"] >= 2
    assert suite["safety_score"] >= 90
    assert "Synthetic deterministic" in suite["demo_note"]
