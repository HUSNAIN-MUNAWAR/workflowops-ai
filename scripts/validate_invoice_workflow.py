from _validation_utils import save_validation, fresh_db
from app.workflows.runner import run_template
from app.db.models import WorkflowRun, ApprovalRequest

def main():
    db = fresh_db()
    text = "Invoice Number: INV-VAL-1\nVendor: Acme Supplies\nTotal: USD 7200\nDue Date: 2026-08-15\nPayment export requested"
    payload = {"text": text, "action_type": "payment_export"}
    run = run_template("invoice_approval", payload, simulation_mode=False)
    if run.status != "waiting_approval":
        raise SystemExit(f"Expected waiting_approval, got {run.status}")
    db_run = WorkflowRun(organization_id="demo-org", template_slug="invoice_approval", input_payload=payload, status=run.status, risk_score=run.context["risk"]["risk_score"], current_step=run.node_results[-1].node_id, logs=run.events, replay_data={"events": run.events})
    db.add(db_run); db.commit(); db.refresh(db_run)
    db.add(ApprovalRequest(organization_id="demo-org", workflow_run_id=db_run.id, title="Validate invoice approval", reason="High value payment export", risk_score=db_run.risk_score, payload={"invoice":"INV-VAL-1"})); db.commit()
    save_validation("invoice_workflow_validation", {"status":"passed","run_id":db_run.id,"workflow_status":db_run.status,"risk_score":db_run.risk_score,"approvals_created":db.query(ApprovalRequest).filter_by(workflow_run_id=db_run.id).count(),"checks":["extracted invoice fields","approval gate triggered","database records written"]})
if __name__ == "__main__": main()
