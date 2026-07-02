from __future__ import annotations
from datetime import datetime
from typing import Any, Literal
from pydantic import BaseModel, ConfigDict, EmailStr, Field

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict[str, Any]

class UserMe(BaseModel):
    id: str
    email: EmailStr
    full_name: str
    role: str
    organization_id: str
    model_config = ConfigDict(from_attributes=True)

class DashboardSummary(BaseModel):
    total_workflow_runs: int
    pending_approvals: int
    failed_automations: int
    average_reliability_score: float
    documents_processed: int
    sla_breaches: int
    template_usage: dict[str, int]

class WorkflowTemplateOut(BaseModel):
    id: str
    slug: str
    name: str
    description: str
    version: str
    risk_threshold: float
    definition_json: dict[str, Any]
    model_config = ConfigDict(from_attributes=True)

class WorkflowRunCreate(BaseModel):
    template_slug: str
    input_payload: dict[str, Any] = Field(default_factory=dict)
    simulation_mode: bool = False
    idempotency_key: str | None = None

class WorkflowRunOut(BaseModel):
    id: str
    template_slug: str
    status: str
    risk_score: float
    current_step: str | None = None
    started_at: datetime
    completed_at: datetime | None = None
    failed_reason: str | None = None
    input_payload: dict[str, Any]
    logs: list[dict[str, Any]]
    replay_data: dict[str, Any]
    model_config = ConfigDict(from_attributes=True)

class WorkflowTimelineStep(BaseModel):
    node_id: str
    node_type: str
    status: str
    retry_count: int
    duration_ms: int
    error_message: str | None = None
    output_snapshot: dict[str, Any]

class ApprovalDecision(BaseModel):
    reason: str = "Reviewed in local demo mode."

class ApprovalOut(BaseModel):
    id: str
    title: str
    reason: str
    status: str
    risk_score: float
    reviewer_role: str
    created_at: datetime
    decided_at: datetime | None = None
    payload: dict[str, Any]
    model_config = ConfigDict(from_attributes=True)

class DocumentOut(BaseModel):
    id: str
    filename: str
    content_type: str
    document_type: str
    classification_confidence: float
    extraction_confidence: float
    warnings: list[str]
    prompt_injection_findings: list[str]
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class ExtractedFieldOut(BaseModel):
    name: str
    value: Any
    confidence: float
    source: str | None = None
    warning: str | None = None
    model_config = ConfigDict(from_attributes=True)

class ReportOut(BaseModel):
    id: str
    title: str
    report_type: str
    summary: str
    paths: dict[str, str]
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class ReliabilityRunCreate(BaseModel):
    template_slug: str = "invoice_approval"

class ReliabilityRunOut(BaseModel):
    id: str
    workflow_template_slug: str
    status: str
    reliability_score: float
    safety_score: float
    failed_cases: int
    replay_logs: list[dict[str, Any]]
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class AuditLogOut(BaseModel):
    id: str
    actor_email: str
    actor_role: str
    action: str
    target_type: str
    target_id: str | None = None
    outcome: str
    request_id: str | None = None
    details: dict[str, Any]
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class QueueJobOut(BaseModel):
    id: str; workflow_run_id: str | None = None; node_id: str | None = None; status: str; attempts: int; last_error: str | None = None; created_at: datetime
    model_config = ConfigDict(from_attributes=True)
class ConnectorActionRequest(BaseModel):
    payload: dict[str, Any] = Field(default_factory=dict); idempotency_key: str | None = None
class ConnectorOut(BaseModel):
    connector_id: str; name: str; category: str; description: str; actions: list[dict[str, Any]]
class ConnectorActionOut(BaseModel):
    connector_id: str; action_name: str; status: str; dry_run: bool; message: str; data: dict[str, Any]
class PolicyOut(BaseModel):
    id: str; name: str; is_default: bool; allowed_template_slugs: list[str]; allowed_connectors: list[str]; workflow_start_roles: list[str]; approval_roles: list[str]; invoice_approval_threshold: float; risk_review_threshold: float; max_retry_count: int; max_workflow_runtime_seconds: int; max_estimated_cost_usd: float; pii_handling_mode: str; prompt_injection_action_mode: str; document_confidence_threshold: float; required_approval_count: int; escalation_rules: dict[str, Any]
    model_config = ConfigDict(from_attributes=True)
class PolicyUpdate(BaseModel):
    allowed_template_slugs: list[str] | None = None; allowed_connectors: list[str] | None = None; workflow_start_roles: list[str] | None = None; approval_roles: list[str] | None = None; invoice_approval_threshold: float | None = None; risk_review_threshold: float | None = None; max_retry_count: int | None = None; max_workflow_runtime_seconds: int | None = None; max_estimated_cost_usd: float | None = None; pii_handling_mode: str | None = None; prompt_injection_action_mode: str | None = None; document_confidence_threshold: float | None = None; required_approval_count: int | None = None; escalation_rules: dict[str, Any] | None = None
class PolicyEvaluateRequest(BaseModel):
    action: str; payload: dict[str, Any] = Field(default_factory=dict)
class PolicyDecisionOut(BaseModel):
    allowed: bool; requires_approval: bool; reason: str; matched_rules: list[str]; required_roles: list[str]; risk_level: str; recommended_action: str
class TemplateValidateRequest(BaseModel): definition_json: dict[str, Any]
class TemplateWriteRequest(BaseModel):
    name: str; slug: str; description: str = "Custom workflow template created in demo builder."; version: str = "1.0.0"; risk_threshold: float = 60; definition_json: dict[str, Any]; is_active: bool = True
class TemplateValidationOut(BaseModel): valid: bool; errors: list[str]
class ReplayRequest(BaseModel): from_node_id: str | None = None
