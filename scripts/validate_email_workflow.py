from _validation_utils import save_validation, fresh_db
from app.workflows.runner import run_template

def main():
    fresh_db()
    text = "Subject: urgent refund complaint\nCustomer says refund deadline tomorrow and legal escalation possible."
    run = run_template("email_to_task", {"text": text, "action_type":"draft_reply"}, simulation_mode=True)
    assert run.status == "completed"
    save_validation("email_workflow_validation", {"status":"passed","workflow_status":run.status,"risk_score":run.context["risk"]["risk_score"],"task":run.context["task"],"checks":["classified email-like input","created task","generated approval-safe draft path"]})
if __name__ == "__main__": main()
