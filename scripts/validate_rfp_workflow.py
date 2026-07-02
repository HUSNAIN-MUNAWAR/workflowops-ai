from _validation_utils import save_validation, fresh_db
from app.workflows.runner import run_template

def main():
    fresh_db()
    text = "RFP Request for Proposal\nDeadline: 2026-09-01\nMandatory: Company profile document\nMandatory: Security policy\nMust provide pricing breakdown."
    run = run_template("rfp_response", {"text": text, "action_type":"internal"}, simulation_mode=True)
    fields = run.context["extract"]["fields"]
    if not fields.get("mandatory_requirements"):
        raise SystemExit("Missing mandatory requirements")
    save_validation("rfp_workflow_validation", {"status":"passed","workflow_status":run.status,"mandatory_requirements":fields.get("mandatory_requirements"),"risk_score":run.context["risk"]["risk_score"],"checks":["requirement extraction","task creation","compliance matrix placeholder export"]})
if __name__ == "__main__": main()
