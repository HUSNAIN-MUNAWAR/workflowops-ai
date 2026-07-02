from app.workflows.runner import run_template


def test_workflow_engine_runs_low_risk_invoice_simulation():
    payload = {"text": "Invoice Number: INV-1\nVendor: Acme Supplies\nTotal: USD 1200\nDue Date: 2026-08-15", "action_type": "internal"}
    run = run_template("invoice_approval", payload, simulation_mode=True)
    assert run.status == "completed"
    assert any(r.node_id == "risk" for r in run.node_results)
    assert run.events
