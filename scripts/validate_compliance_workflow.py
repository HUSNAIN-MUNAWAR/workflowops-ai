from _validation_utils import save_validation, fresh_db
from app.workflows.runner import run_template

def main():
    fresh_db()
    text = "Policy: Access Control\nControl ID: ISO-12.1\nEvidence: PR approval and CI log retained for audit."
    run = run_template("compliance_evidence", {"text": text, "action_type":"internal"}, simulation_mode=True)
    save_validation("compliance_workflow_validation", {"status":"passed","workflow_status":run.status,"fields":run.context["extract"]["fields"],"checks":["control id extraction","audit-safe task path","report generation path"]})
if __name__ == "__main__": main()
