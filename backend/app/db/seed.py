from __future__ import annotations
from types import SimpleNamespace
from pathlib import Path
from sqlalchemy.orm import Session
from app.core.security import hash_password, detect_prompt_injection
from app.db.models import Organization, User, WorkflowTemplate, WorkflowRun, WorkflowStepRun, Task, ApprovalRequest, Document, ExtractedField, AuditLog, Report, ReliabilityTestRun, ReliabilityTestCaseResult, OrganizationPolicy, utcnow
from app.workflows.templates import load_builtin_templates
from app.modules.reliability.evalbench import run_reliability_suite


def build_demo_seed():
    org = SimpleNamespace(org_id="demo-org", name="WorkflowOps Demo Organization", slug="workflowops-demo")
    users = [
        SimpleNamespace(email="admin@example.com", role="admin", full_name="Admin User"),
        SimpleNamespace(email="manager@example.com", role="automation_manager", full_name="Automation Manager"),
        SimpleNamespace(email="reviewer@example.com", role="reviewer", full_name="Reviewer User"),
        SimpleNamespace(email="viewer@example.com", role="viewer", full_name="Viewer User"),
    ]
    return {"organization": org, "users": users, "templates": load_builtin_templates()}


def seed_database(db: Session, reset: bool = False) -> dict[str, int]:
    if reset:
        for model in [ReliabilityTestCaseResult, ReliabilityTestRun, ExtractedField, Document, ApprovalRequest, Task, WorkflowStepRun, WorkflowRun, Report, AuditLog, WorkflowTemplate, User, Organization]:
            db.query(model).delete()
        db.commit()
    org = db.query(Organization).filter_by(slug="workflowops-demo").first()
    if not org:
        org = Organization(id="demo-org", name="WorkflowOps Demo Organization", slug="workflowops-demo")
        db.add(org); db.commit(); db.refresh(org)
    users = [
        ("admin@example.com", "Admin User", "admin", "admin123"),
        ("manager@example.com", "Automation Manager", "automation_manager", "manager123"),
        ("reviewer@example.com", "Reviewer User", "reviewer", "reviewer123"),
        ("viewer@example.com", "Viewer User", "viewer", "viewer123"),
    ]
    for email, name, role, password in users:
        if not db.query(User).filter_by(email=email).first():
            db.add(User(organization_id=org.id, email=email, full_name=name, role=role, password_hash=hash_password(password)))
    db.commit()
    if not db.query(OrganizationPolicy).filter_by(organization_id=org.id, is_default=True).first():
        db.add(OrganizationPolicy(organization_id=org.id, allowed_template_slugs=[t.slug for t in load_builtin_templates()], allowed_connectors=["email_demo","slack_demo","sheets_demo","crm_demo","accounting_demo","webhook_demo","file_demo"], escalation_rules={"vip":"reviewer","legal":"admin"}))
        db.commit()
    for template in load_builtin_templates():
        row = db.query(WorkflowTemplate).filter_by(organization_id=org.id, slug=template.slug).first()
        if not row:
            db.add(WorkflowTemplate(organization_id=org.id, slug=template.slug, name=template.name, description=template.description, version=template.version, risk_threshold=template.risk_threshold, definition_json=template.as_definition()))
    db.commit()
    if not db.query(Document).first():
        invoice_text = Path('demo_data/invoices/invoice_ok.txt').read_text(encoding='utf-8') if Path('demo_data/invoices/invoice_ok.txt').exists() else "Invoice Number: INV-1001\nVendor: Acme Supplies\nTotal: USD 1250\nDue Date: 2026-08-15"
        doc = Document(organization_id=org.id, filename="synthetic_invoice_INV-1001.txt", content_type="text/plain", text_content=invoice_text, document_type="invoice", classification_confidence=0.92, extraction_confidence=0.91, warnings=[], prompt_injection_findings=detect_prompt_injection(invoice_text))
        db.add(doc); db.commit(); db.refresh(doc)
        for name, value in {"vendor":"Acme Supplies","invoice_number":"INV-1001","total":1250,"currency":"USD","due_date":"2026-08-15"}.items():
            db.add(ExtractedField(document_id=doc.id, name=name, value=value, confidence=0.9, source="synthetic_invoice"))
        run = WorkflowRun(organization_id=org.id, template_id=None, template_slug="invoice_approval", input_payload={"document_id": doc.id, "action_type":"payment_export"}, status="waiting_approval", risk_score=72.0, current_step="approval", logs=[{"event":"seeded_demo_run"}], replay_data={"from_step":"approval", "events":["ingest","classify","extract","risk","approval"]})
        db.add(run); db.commit(); db.refresh(run)
        steps=[("ingest","ingest_document","completed"),("classify","classify_document","completed"),("extract","extract_fields","completed"),("validate","validate_fields","completed"),("risk","score_risk","completed"),("approval","request_approval","waiting_approval")]
        for i,(node_id,node_type,status) in enumerate(steps):
            db.add(WorkflowStepRun(workflow_run_id=run.id, node_id=node_id, node_type=node_type, status=status, input_snapshot={}, output_snapshot={"order":i}, duration_ms=20+i))
        db.add(Task(organization_id=org.id, workflow_run_id=run.id, title="Review invoice INV-1001 payment export", department="Finance", assignee_email="reviewer@example.com", priority="high", metadata_json={"source":"seed"}))
        db.add(ApprovalRequest(organization_id=org.id, workflow_run_id=run.id, title="Approve invoice payment export", reason="Risk score exceeds threshold and external finance export is requested.", status="pending", risk_score=72.0, requested_by="system", reviewer_role="reviewer", payload={"invoice_number":"INV-1001","amount":1250}))
        db.add(Report(organization_id=org.id, workflow_run_id=run.id, title="Invoice Exception Report", report_type="invoice_exception", summary="Synthetic seeded invoice report", paths={"json":"sample_outputs/reports/invoice_exception_report.json","markdown":"sample_outputs/reports/invoice_exception_report.md","html":"sample_outputs/reports/invoice_exception_report.html","pdf":"sample_outputs/reports/invoice_exception_report.pdf"}, data={"summary":"Synthetic seeded invoice report"}))
        rel = run_reliability_suite()
        tr = ReliabilityTestRun(organization_id=org.id, workflow_template_slug="invoice_approval", status="completed", reliability_score=rel["reliability_score"], safety_score=rel["safety_score"], failed_cases=rel["failed_count"], replay_logs=rel["replay_logs"], report_paths={}, )
        db.add(tr); db.commit(); db.refresh(tr)
        for case in rel["cases"]:
            db.add(ReliabilityTestCaseResult(reliability_test_run_id=tr.id, test_name=case["test_name"], scenario_type=case["scenario_type"], input_mutation=case["input_mutation"], expected_behavior=case["expected_behavior"], actual_behavior=case["actual_behavior"], passed=case["passed"], severity=case["severity"], evidence={"items": case["evidence"]}, mitigation_recommendation=case["mitigation_recommendation"]))
        db.add(AuditLog(organization_id=org.id, actor_email="system", actor_role="system", action="demo.seed.completed", target_type="organization", target_id=org.id, outcome="success", details={"synthetic": True}))
        db.commit()
    return {"organizations": db.query(Organization).count(), "users": db.query(User).count(), "templates": db.query(WorkflowTemplate).count(), "runs": db.query(WorkflowRun).count(), "approvals": db.query(ApprovalRequest).count()}
