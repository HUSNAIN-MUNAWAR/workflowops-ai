from __future__ import annotations
from pathlib import Path
from _validation_utils import save_validation
from app.reports.generator import generate_report
ROOT=Path(__file__).resolve().parents[1]
REPORT_DIR=ROOT/'sample_outputs/reports'
BASE={
 'input_files':['synthetic demo file(s)'],
 'extracted_fields':{'document_type':'synthetic demo'},
 'risk_score':72,
 'decisions_made':['Created task','Required approval when risk/action policy demanded it'],
 'approval_history':['Pending/approved records are synthetic demo data'],
 'audit_events':['workflow.run.created','approval.approved/rejected','report.downloaded'],
 'recommendations':['Wire real business systems only after scoped security review'],
 'limitations':['Synthetic validation only','Not certified accounting/legal/compliance software']
}
REPORTS=[
 ('Invoice Exception Report','invoice_exception_report','Mismatch or high-risk invoice cases are routed to finance review.'),
 ('RFP Compliance Matrix','rfp_compliance_matrix','Mandatory requirements and missing documents are summarized for proposal teams.'),
 ('Compliance Evidence Pack','compliance_evidence_pack','Synthetic controls are mapped to local evidence records.'),
 ('Customer Escalation Report','customer_escalation_summary','High-risk support messages are summarized with recommended escalation.'),
 ('Workflow Reliability Test Report','workflow_reliability_test_report','Workflow EvalBench reports reliability and safety scenario outcomes.'),
 ('Weekly Automation Operations Report','weekly_automation_operations_report','Weekly synthetic operations snapshot for processed documents, approvals, and failures.'),
]
def main():
    index=[]
    for title, slug, summary in REPORTS:
        payload=dict(BASE); payload.update({'slug':slug,'executive_summary':summary})
        paths=generate_report(title,payload,REPORT_DIR)
        index.append({'title':title,'slug':slug,'paths':paths})
    save_validation('generated_reports_index', {'status':'passed','reports_generated':len(index),'reports':[i['slug'] for i in index], 'paths':{i['slug']:i['paths'] for i in index}})
if __name__=='__main__': main()
