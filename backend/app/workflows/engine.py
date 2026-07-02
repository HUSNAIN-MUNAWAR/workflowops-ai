from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable
from uuid import uuid4

from app.core.audit import AuditLogger
from app.core.security import detect_prompt_injection, redact_text
from app.documents.classifier import classify_document
from app.documents.extraction import extract_key_values, confidence_score
from app.workflows.approvals import ApprovalRequest, should_request_approval
from app.workflows.nodes import NodeResult, NodeStatus, WorkflowNode
from app.workflows.templates import WorkflowTemplate

Handler = Callable[[dict[str, Any], WorkflowNode], dict[str, Any]]


@dataclass
class WorkflowRun:
    template_slug: str
    run_id: str = field(default_factory=lambda: str(uuid4()))
    status: str = "pending"
    context: dict[str, Any] = field(default_factory=dict)
    node_results: list[NodeResult] = field(default_factory=list)
    events: list[dict[str, Any]] = field(default_factory=list)
    approvals: list[ApprovalRequest] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    completed_at: str | None = None


class WorkflowEngine:
    def __init__(self, audit_logger: AuditLogger | None = None, simulation_mode: bool = False) -> None:
        self.audit = audit_logger or AuditLogger()
        self.simulation_mode = simulation_mode
        self.handlers: dict[str, Handler] = {
            "ingest_document": self._ingest,
            "classify_document": self._classify,
            "extract_fields": self._extract,
            "validate_fields": self._validate,
            "risk_score": self._risk_score,
            "score_risk": self._risk_score,
            "create_task": self._create_task,
            "request_approval": self._request_approval,
            "send_draft": self._send_draft,
            "generate_draft_reply": self._send_draft,
            "generate_draft": self._send_draft,
            "connector_action": self._connector_action,
            "branch": self._branch,
            "merge": self._merge,
            "stop": self._close_case,
            "export_report": self._export_report,
            "generate_report": self._export_report,
            "export_data": self._export_report,
            "notify_user": self._notify_user,
            "notify_user_stub": self._notify_user,
            "wait_for_human": self._request_approval,
            "retry_step": self._retry_step,
            "close_case": self._close_case,
            "stop_workflow": self._close_case,
            "generate_test_scenarios": self._generate_test_scenarios,
            "simulate_workflow": self._simulate_workflow,
            "detect_failures": self._detect_failures,
            "build_replay": self._build_replay,
        }

    def run(self, template: WorkflowTemplate, input_payload: dict[str, Any], actor: str = "system") -> WorkflowRun:
        run = WorkflowRun(template_slug=template.slug, context={"input": input_payload})
        run.status = "running"
        self._event(run, "run_started", status="running", template=template.slug)
        self.audit.record(actor, "workflow.run.started", run.run_id, template=template.slug, simulation=self.simulation_mode)

        for node in template.nodes:
            handler = self.handlers.get(node.node_type)
            if not handler:
                result = NodeResult(node.node_id, NodeStatus.FAILED, {}, f"Unsupported node type {node.node_type}")
                run.node_results.append(result)
                run.status = "failed"
                self._event(run, node.node_id, status="failed", error=result.error)
                break
            attempts = 0
            while attempts <= node.retry_limit:
                attempts += 1
                try:
                    self._event(run, node.node_id, status="running", node_type=node.node_type, attempt=attempts)
                    output = handler(run.context, node)
                    status = NodeStatus.WAITING_APPROVAL if output.get("approval_required") else NodeStatus.COMPLETED
                    result = NodeResult(node.node_id, status, output, attempts=attempts)
                    run.node_results.append(result)
                    run.context[node.node_id] = output
                    self._event(run, node.node_id, status=status.value, output_summary=list(output.keys()))
                    self.audit.record(actor, "workflow.node.completed", run.run_id, node=node.node_id, status=status.value)
                    if status == NodeStatus.WAITING_APPROVAL and not self.simulation_mode:
                        run.status = "waiting_approval"
                        run.completed_at = datetime.now(timezone.utc).isoformat()
                        return run
                    break
                except Exception as exc:
                    if attempts > node.retry_limit:
                        result = NodeResult(node.node_id, NodeStatus.FAILED, {}, str(exc), attempts=attempts)
                        run.node_results.append(result)
                        run.status = "failed"
                        self._event(run, node.node_id, status="failed", error=str(exc), attempts=attempts)
                        self.audit.record(actor, "workflow.node.failed", run.run_id, node=node.node_id, error=str(exc))
                        run.completed_at = datetime.now(timezone.utc).isoformat()
                        return run
        if run.status not in {"failed", "waiting_approval"}:
            run.status = "completed"
            run.completed_at = datetime.now(timezone.utc).isoformat()
            self._event(run, "run_completed", status="completed")
            self.audit.record(actor, "workflow.run.completed", run.run_id, template=template.slug)
        return run

    def _event(self, run: WorkflowRun, event: str, **payload: Any) -> None:
        run.events.append({"ts": datetime.now(timezone.utc).isoformat(), "event": event, **payload})

    def _ingest(self, context: dict[str, Any], node: WorkflowNode) -> dict[str, Any]:
        payload = context["input"]
        text = payload.get("text") or payload.get("body") or payload.get("document_text") or ""
        redacted = redact_text(text)
        prompt_findings = detect_prompt_injection(text)
        return {"text": redacted, "filename": payload.get("filename", "synthetic_input.txt"), "prompt_injection_findings": prompt_findings}

    def _classify(self, context: dict[str, Any], node: WorkflowNode) -> dict[str, Any]:
        result = classify_document(context["ingest"]["text"])
        return result.__dict__

    def _extract(self, context: dict[str, Any], node: WorkflowNode) -> dict[str, Any]:
        fields = extract_key_values(context["ingest"]["text"])
        doc_type = context.get("classify", {}).get("document_type", "general_business_document")
        required_map = {
            "invoice": ["vendor", "invoice_number", "total", "due_date"],
            "rfp": ["deadline", "mandatory_documents"],
            "policy_document": ["control_id", "evidence"],
        }
        required = required_map.get(doc_type, [])
        return {"document_type": doc_type, "fields": fields, "confidence": confidence_score(fields, required), "required_fields": required}

    def _validate(self, context: dict[str, Any], node: WorkflowNode) -> dict[str, Any]:
        extracted = context["extract"]
        fields = extracted["fields"]
        missing = [field for field in extracted.get("required_fields", []) if not fields.get(field)]
        return {"valid": not missing, "missing_fields": missing, "field_count": len(fields)}

    def _risk_score(self, context: dict[str, Any], node: WorkflowNode) -> dict[str, Any]:
        score = 10.0
        if context["ingest"].get("prompt_injection_findings"):
            score += 45
        if not context.get("validate", {}).get("valid", True):
            score += 25
        confidence = context.get("extract", {}).get("confidence", 1.0)
        score += max(0, (1 - confidence) * 30)
        text = context["ingest"].get("text", "").lower()
        if any(k in text for k in ["payment", "refund", "legal", "contract", "vendor bank", "angry", "urgent", "vip", "complaint"]):
            score += 15
        if context.get("extract", {}).get("fields", {}).get("support_risk_terms"):
            score += 20
        score = round(min(score, 100.0), 2)
        return {"risk_score": score, "risk_level": "high" if score >= 70 else "medium" if score >= 40 else "low"}

    def _create_task(self, context: dict[str, Any], node: WorkflowNode) -> dict[str, Any]:
        doc_type = context.get("classify", {}).get("document_type", "general")
        department = {
            "invoice": "Finance", "rfp": "Sales", "policy_document": "Security", "support_attachment": "Support"
        }.get(doc_type, "Operations")
        return {"task_title": f"Review {doc_type} automation output", "department": department, "status": "open"}

    def _request_approval(self, context: dict[str, Any], node: WorkflowNode) -> dict[str, Any]:
        risk = context.get("risk", {}).get("risk_score", 0)
        action_type = context["input"].get("action_type", "internal")
        threshold = float(node.config.get("risk_threshold", 65))
        required = should_request_approval(risk, threshold, action_type)
        if required:
            request = ApprovalRequest(
                title=f"Approval required for {context.get('task', {}).get('task_title', 'workflow action')}",
                reason=f"Risk score {risk} or sensitive action {action_type}",
                risk_score=risk,
            )
            return {"approval_required": True, "approval": request.__dict__}
        return {"approval_required": False, "decision": "auto_continue", "reason": "Risk below threshold and internal action."}

    def _send_draft(self, context: dict[str, Any], node: WorkflowNode) -> dict[str, Any]:
        if not self.simulation_mode:
            return {"draft_created": True, "sent": False, "reason": "External sending disabled without human approval."}
        return {"draft_created": True, "sent": False, "simulation": True}

    def _export_report(self, context: dict[str, Any], node: WorkflowNode) -> dict[str, Any]:
        return {"report_ready": True, "formats": ["json", "markdown", "html"], "pdf_feasible": True}

    def _branch(self, context, node):
        risk=context.get("risk",{}).get("risk_score",0); return {"branch":"high_risk" if risk>=45 else "standard","risk_score":risk}

    def _merge(self, context, node):
        return {"merged": True}

    def _connector_action(self, context, node):
        return {"connector_id":node.config.get("connector_id","demo"),"action":node.config.get("action","demo"),"executed":False,"dry_run":True}

    def _notify_user(self, context: dict[str, Any], node: WorkflowNode) -> dict[str, Any]:
        return {"notification": "queued", "channel": "dashboard"}

    def _retry_step(self, context: dict[str, Any], node: WorkflowNode) -> dict[str, Any]:
        return {"retry_policy": "max_attempts", "retry_limit": node.retry_limit}

    def _close_case(self, context: dict[str, Any], node: WorkflowNode) -> dict[str, Any]:
        return {"closed": True, "summary": "Workflow completed or waiting for human decision."}

    def _generate_test_scenarios(self, context: dict[str, Any], node: WorkflowNode) -> dict[str, Any]:
        return {"scenarios": ["missing_input_fields", "prompt_injection", "approval_bypass_attempt", "api_timeout"]}

    def _simulate_workflow(self, context: dict[str, Any], node: WorkflowNode) -> dict[str, Any]:
        scenarios = context.get("scenario", {}).get("scenarios", [])
        return {"simulated": len(scenarios), "failures": [s for s in scenarios if s != "api_timeout"]}

    def _detect_failures(self, context: dict[str, Any], node: WorkflowNode) -> dict[str, Any]:
        failures = context.get("simulate", {}).get("failures", [])
        return {"failure_count": len(failures), "failed_scenarios": failures, "score": max(0, 100 - 12 * len(failures))}

    def _build_replay(self, context: dict[str, Any], node: WorkflowNode) -> dict[str, Any]:
        return {"replay_available": True, "events": len(context)}
