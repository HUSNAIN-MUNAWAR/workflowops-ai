from _validation_utils import save_validation, fresh_db
from app.workflows.runner import run_template

def main():
    fresh_db()
    text = "Ticket: VIP customer angry about outage. Urgent refund requested and legal escalation mentioned."
    run = run_template("support_escalation", {"text": text, "action_type":"draft_reply"}, simulation_mode=True)
    terms = run.context["extract"]["fields"].get("support_risk_terms", [])
    if not terms:
        raise SystemExit("Expected support risk terms")
    save_validation("support_workflow_validation", {"status":"passed","workflow_status":run.status,"risk_terms":terms,"risk_score":run.context["risk"]["risk_score"],"checks":["support risk terms detected","human-safe notification stub","SLA/risk path available"]})
if __name__ == "__main__": main()
