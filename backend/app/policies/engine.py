
from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Any
from sqlalchemy.orm import Session
from app.db.models import AuditLog, OrganizationPolicy, User
@dataclass
class PolicyDecision:
    allowed: bool; requires_approval: bool; reason: str; matched_rules: list[str]; required_roles: list[str]; risk_level: str; recommended_action: str
    def dict(self): return asdict(self)
def ensure_default_policy(db:Session,organization_id:str)->OrganizationPolicy:
    row=db.query(OrganizationPolicy).filter_by(organization_id=organization_id,is_default=True).first()
    if row: return row
    row=OrganizationPolicy(organization_id=organization_id,allowed_template_slugs=["invoice_approval","email_to_task","rfp_response","compliance_evidence","support_escalation","workflow_reliability"],allowed_connectors=["email_demo","slack_demo","sheets_demo","crm_demo","accounting_demo","webhook_demo","file_demo"],escalation_rules={"vip":"reviewer","legal":"admin"})
    db.add(row); db.commit(); db.refresh(row); return row
def evaluate_policy(db:Session,organization_id:str,*,actor:User|None=None,action:str,payload:dict[str,Any]|None=None)->PolicyDecision:
    payload=payload or {}; policy=ensure_default_policy(db,organization_id); matched=[]; allowed=True; requires=False; reason="Allowed by default demo policy."; risk=float(payload.get("risk_score") or 0); amount=float(payload.get("amount") or payload.get("total") or payload.get("invoice_amount") or 0); confidence=float(payload.get("confidence") or payload.get("extraction_confidence") or 1); connector_id=payload.get("connector_id"); template_slug=payload.get("template_slug")
    if action=="start_workflow":
        matched.append("workflow_start_roles"); roles=policy.workflow_start_roles or ["admin","automation_manager"]
        if actor and actor.role not in roles and actor.role!="admin": allowed=False; reason="Actor role is not allowed to start workflows."
        if template_slug and policy.allowed_template_slugs and template_slug not in policy.allowed_template_slugs: allowed=False; matched.append("allowed_template_slugs"); reason="Workflow template is not allowed by tenant policy."
    if connector_id:
        matched.append("allowed_connectors")
        if policy.allowed_connectors and connector_id not in policy.allowed_connectors: allowed=False; reason="Connector is not allowlisted by tenant policy."
    if amount>policy.invoice_approval_threshold: requires=True; matched.append("invoice_approval_threshold"); reason=f"Invoice amount {amount} exceeds approval threshold {policy.invoice_approval_threshold}."
    if risk>=policy.risk_review_threshold: requires=True; matched.append("risk_review_threshold"); reason=f"Risk score {risk} requires human review."
    if confidence<policy.document_confidence_threshold: requires=True; matched.append("document_confidence_threshold"); reason="Low extraction confidence requires human review."
    if payload.get("prompt_injection_detected"):
        matched.append("prompt_injection_action_mode")
        if policy.prompt_injection_action_mode in {"block","quarantine"}: allowed=False; reason="Prompt injection indicator detected; action blocked/quarantined by policy."
    if float(payload.get("estimated_cost_usd") or 0)>policy.max_estimated_cost_usd: allowed=False; matched.append("max_estimated_cost_usd"); reason="Estimated cost exceeds tenant budget guard."
    if action.startswith("connector_execute") and payload.get("high_risk",True): requires=True; matched.append("external_action_allowlist"); reason="High-risk connector execution requires approval."
    level="high" if risk>=70 or not allowed else "medium" if requires or risk>=40 else "low"; recommended="block" if not allowed else "request_approval" if requires else "continue"
    db.add(AuditLog(organization_id=organization_id,actor_email=actor.email if actor else "system",actor_role=actor.role if actor else "system",action="policy_blocked" if not allowed else "policy_allowed",target_type="policy",outcome="blocked" if not allowed else "success",details={"action":action,"matched_rules":matched,"reason":reason,"payload_keys":list(payload.keys())})); db.commit()
    return PolicyDecision(allowed,requires,reason,matched,policy.approval_roles or ["admin","reviewer"],level,recommended)
def update_policy(db:Session,organization_id:str,values:dict[str,Any])->OrganizationPolicy:
    policy=ensure_default_policy(db,organization_id)
    for k,v in values.items():
        if hasattr(policy,k): setattr(policy,k,v)
    db.commit(); db.refresh(policy); return policy
