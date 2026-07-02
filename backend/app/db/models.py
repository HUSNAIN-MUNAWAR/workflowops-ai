from __future__ import annotations
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, JSON, String, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

def utcnow() -> datetime:
    return datetime.now(timezone.utc)

def uuid_str() -> str:
    return str(uuid4())

def now() -> str:
    return utcnow().isoformat()

class Base(DeclarativeBase):
    pass

class Organization(Base):
    __tablename__ = "organizations"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(120), unique=True, nullable=False, default="workflowops-demo")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    users: Mapped[list["User"]] = relationship(back_populates="organization")

class User(Base):
    __tablename__ = "users"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    organization: Mapped[Organization] = relationship(back_populates="users")

class WorkflowTemplate(Base):
    __tablename__ = "workflow_templates"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    slug: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    version: Mapped[str] = mapped_column(String(50), default="1.0.0")
    risk_threshold: Mapped[float] = mapped_column(Float, default=65.0)
    definition_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    __table_args__ = (UniqueConstraint("organization_id", "slug", name="uq_template_org_slug"),)

class WorkflowRun(Base):
    __tablename__ = "workflow_runs"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"), nullable=False, index=True)
    template_id: Mapped[str | None] = mapped_column(ForeignKey("workflow_templates.id"), nullable=True)
    template_slug: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    input_payload: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    status: Mapped[str] = mapped_column(String(50), default="pending", index=True)
    risk_score: Mapped[float] = mapped_column(Float, default=0.0)
    current_step: Mapped[str | None] = mapped_column(String(120), nullable=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    failed_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    logs: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default=list)
    replay_data: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    simulation_mode: Mapped[bool] = mapped_column(Boolean, default=False)
    idempotency_key: Mapped[str | None] = mapped_column(String(120), nullable=True, index=True)
    steps: Mapped[list["WorkflowStepRun"]] = relationship(back_populates="workflow_run", cascade="all, delete-orphan")
    approvals: Mapped[list["ApprovalRequest"]] = relationship(back_populates="workflow_run")

class WorkflowStepRun(Base):
    __tablename__ = "workflow_step_runs"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    workflow_run_id: Mapped[str] = mapped_column(ForeignKey("workflow_runs.id"), nullable=False, index=True)
    node_id: Mapped[str] = mapped_column(String(120), nullable=False)
    node_type: Mapped[str] = mapped_column(String(120), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="pending")
    input_snapshot: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    output_snapshot: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    duration_ms: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    workflow_run: Mapped[WorkflowRun] = relationship(back_populates="steps")

class Task(Base):
    __tablename__ = "tasks"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"), nullable=False, index=True)
    workflow_run_id: Mapped[str | None] = mapped_column(ForeignKey("workflow_runs.id"), nullable=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    department: Mapped[str] = mapped_column(String(120), nullable=False)
    assignee_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="open")
    due_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    priority: Mapped[str] = mapped_column(String(50), default="normal")
    metadata_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

class ApprovalRequest(Base):
    __tablename__ = "approval_requests"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"), nullable=False, index=True)
    workflow_run_id: Mapped[str | None] = mapped_column(ForeignKey("workflow_runs.id"), nullable=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="pending", index=True)
    risk_score: Mapped[float] = mapped_column(Float, default=0.0)
    requested_by: Mapped[str] = mapped_column(String(255), default="system")
    reviewer_role: Mapped[str] = mapped_column(String(50), default="reviewer")
    decision_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
    decision_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    decided_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    payload: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    workflow_run: Mapped[WorkflowRun | None] = relationship(back_populates="approvals")

class Document(Base):
    __tablename__ = "documents"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"), nullable=False, index=True)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    content_type: Mapped[str] = mapped_column(String(120), default="text/plain")
    storage_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    text_content: Mapped[str] = mapped_column(Text, default="")
    document_type: Mapped[str] = mapped_column(String(120), default="general_business_document")
    classification_confidence: Mapped[float] = mapped_column(Float, default=0.0)
    extraction_confidence: Mapped[float] = mapped_column(Float, default=0.0)
    warnings: Mapped[list[str]] = mapped_column(JSON, default=list)
    prompt_injection_findings: Mapped[list[str]] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    fields: Mapped[list["ExtractedField"]] = relationship(back_populates="document", cascade="all, delete-orphan")

class ExtractedField(Base):
    __tablename__ = "extracted_fields"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    document_id: Mapped[str] = mapped_column(ForeignKey("documents.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    value: Mapped[Any] = mapped_column(JSON, nullable=True)
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    source: Mapped[str | None] = mapped_column(Text, nullable=True)
    warning: Mapped[str | None] = mapped_column(Text, nullable=True)
    document: Mapped[Document] = relationship(back_populates="fields")

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    organization_id: Mapped[str | None] = mapped_column(ForeignKey("organizations.id"), nullable=True, index=True)
    actor_email: Mapped[str] = mapped_column(String(255), default="system")
    actor_role: Mapped[str] = mapped_column(String(50), default="system")
    action: Mapped[str] = mapped_column(String(160), nullable=False, index=True)
    target_type: Mapped[str] = mapped_column(String(120), default="system")
    target_id: Mapped[str | None] = mapped_column(String(120), nullable=True)
    outcome: Mapped[str] = mapped_column(String(50), default="success")
    request_id: Mapped[str | None] = mapped_column(String(80), nullable=True)
    details: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, index=True)

class Report(Base):
    __tablename__ = "reports"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"), nullable=False, index=True)
    workflow_run_id: Mapped[str | None] = mapped_column(ForeignKey("workflow_runs.id"), nullable=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    report_type: Mapped[str] = mapped_column(String(120), nullable=False)
    summary: Mapped[str] = mapped_column(Text, default="")
    data: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    paths: Mapped[dict[str, str]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

class ReliabilityTestRun(Base):
    __tablename__ = "reliability_test_runs"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"), nullable=False, index=True)
    workflow_template_slug: Mapped[str] = mapped_column(String(120), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="completed")
    reliability_score: Mapped[float] = mapped_column(Float, default=0.0)
    safety_score: Mapped[float] = mapped_column(Float, default=0.0)
    failed_cases: Mapped[int] = mapped_column(Integer, default=0)
    report_paths: Mapped[dict[str, str]] = mapped_column(JSON, default=dict)
    replay_logs: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    case_results: Mapped[list["ReliabilityTestCaseResult"]] = relationship(back_populates="test_run", cascade="all, delete-orphan")

class ReliabilityTestCaseResult(Base):
    __tablename__ = "reliability_test_case_results"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    reliability_test_run_id: Mapped[str] = mapped_column(ForeignKey("reliability_test_runs.id"), nullable=False, index=True)
    test_name: Mapped[str] = mapped_column(String(255), nullable=False)
    scenario_type: Mapped[str] = mapped_column(String(120), nullable=False)
    input_mutation: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    expected_behavior: Mapped[str] = mapped_column(Text, nullable=False)
    actual_behavior: Mapped[str] = mapped_column(Text, nullable=False)
    passed: Mapped[bool] = mapped_column(Boolean, default=False)
    severity: Mapped[str] = mapped_column(String(50), default="medium")
    evidence: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    mitigation_recommendation: Mapped[str] = mapped_column(Text, default="")
    test_run: Mapped[ReliabilityTestRun] = relationship(back_populates="case_results")

WorkflowTemplateRecord = WorkflowTemplate
WorkflowRunRecord = WorkflowRun
TaskRecord = Task
ApprovalRecord = ApprovalRequest
DocumentRecord = Document
ExtractedFieldRecord = ExtractedField
ReportRecord = Report
ReliabilityTestRecord = ReliabilityTestRun


class OrganizationPolicy(Base):
    __tablename__ = "organization_policies"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(160), default="Default Governance Policy")
    is_default: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    allowed_template_slugs: Mapped[list[str]] = mapped_column(JSON, default=list)
    allowed_connectors: Mapped[list[str]] = mapped_column(JSON, default=list)
    workflow_start_roles: Mapped[list[str]] = mapped_column(JSON, default=lambda: ["admin", "automation_manager"])
    approval_roles: Mapped[list[str]] = mapped_column(JSON, default=lambda: ["admin", "reviewer"])
    invoice_approval_threshold: Mapped[float] = mapped_column(Float, default=1000.0)
    risk_review_threshold: Mapped[float] = mapped_column(Float, default=60.0)
    max_retry_count: Mapped[int] = mapped_column(Integer, default=2)
    max_workflow_runtime_seconds: Mapped[int] = mapped_column(Integer, default=180)
    max_estimated_cost_usd: Mapped[float] = mapped_column(Float, default=2.0)
    pii_handling_mode: Mapped[str] = mapped_column(String(80), default="redact")
    prompt_injection_action_mode: Mapped[str] = mapped_column(String(80), default="quarantine")
    document_confidence_threshold: Mapped[float] = mapped_column(Float, default=0.72)
    required_approval_count: Mapped[int] = mapped_column(Integer, default=1)
    escalation_rules: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

class ConnectorActionLog(Base):
    __tablename__ = "connector_action_logs"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"), nullable=False, index=True)
    connector_id: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    action_name: Mapped[str] = mapped_column(String(120), nullable=False)
    mode: Mapped[str] = mapped_column(String(40), default="dry_run")
    status: Mapped[str] = mapped_column(String(60), default="simulated")
    requires_approval: Mapped[bool] = mapped_column(Boolean, default=True)
    idempotency_key: Mapped[str | None] = mapped_column(String(160), nullable=True, index=True)
    request_payload: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    response_payload: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

class QueueJob(Base):
    __tablename__ = "queue_jobs"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    organization_id: Mapped[str | None] = mapped_column(ForeignKey("organizations.id"), nullable=True, index=True)
    workflow_run_id: Mapped[str | None] = mapped_column(ForeignKey("workflow_runs.id"), nullable=True, index=True)
    node_id: Mapped[str | None] = mapped_column(String(120), nullable=True)
    queue_name: Mapped[str] = mapped_column(String(120), default="workflowops")
    status: Mapped[str] = mapped_column(String(60), default="queued", index=True)
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    max_attempts: Mapped[int] = mapped_column(Integer, default=3)
    last_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    rq_job_id: Mapped[str | None] = mapped_column(String(160), nullable=True)
    heartbeat_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

class DemoEmailDraft(Base):
    __tablename__ = "demo_email_drafts"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"), nullable=False, index=True)
    to_email: Mapped[str] = mapped_column(String(255), nullable=False)
    subject: Mapped[str] = mapped_column(String(255), nullable=False)
    body: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(60), default="draft")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
class DemoNotification(Base):
    __tablename__ = "demo_notifications"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"), nullable=False, index=True)
    channel: Mapped[str] = mapped_column(String(120), default="demo-slack")
    message: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
class DemoSheetRow(Base):
    __tablename__ = "demo_sheet_rows"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"), nullable=False, index=True)
    sheet_name: Mapped[str] = mapped_column(String(160), default="workflowops_demo")
    row_data: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
class DemoCRMRecord(Base):
    __tablename__ = "demo_crm_records"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"), nullable=False, index=True)
    record_type: Mapped[str] = mapped_column(String(80), default="task")
    record_data: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
class DemoAccountingExport(Base):
    __tablename__ = "demo_accounting_exports"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"), nullable=False, index=True)
    export_type: Mapped[str] = mapped_column(String(80), default="invoice")
    export_data: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
class DemoFileObject(Base):
    __tablename__ = "demo_file_objects"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"), nullable=False, index=True)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    storage_path: Mapped[str] = mapped_column(Text, nullable=False)
    metadata_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
