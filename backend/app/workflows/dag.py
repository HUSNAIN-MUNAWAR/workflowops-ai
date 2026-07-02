
from __future__ import annotations
from collections import defaultdict, deque
from datetime import datetime, timezone
from time import perf_counter
from typing import Any
from sqlalchemy.orm import Session
from app.core.security import detect_prompt_injection, redact_text
from app.db.models import ApprovalRequest, AuditLog, Report, Task, WorkflowRun, WorkflowStepRun, WorkflowTemplate
from app.documents.classifier import classify_document
from app.documents.extraction import confidence_score, extract_key_values
from app.policies.engine import evaluate_policy
from app.reports.generator import build_report_payload
def _now(): return datetime.now(timezone.utc)
def validate_dag(definition:dict[str,Any])->list[str]:
    errors=[]; nodes=definition.get("nodes") or []; node_ids=[n.get("node_id") for n in nodes]; known=set(node_ids)
    if not nodes: errors.append("Template must include at least one node.")
    if len(set(node_ids))!=len(node_ids): errors.append("Duplicate node_id detected.")
    graph=defaultdict(list); indeg={n:0 for n in node_ids}
    for e in definition.get("edges") or []:
        a,b=e.get("from"),e.get("to")
        if a not in known or b not in known: errors.append(f"Edge references missing node: {a}->{b}"); continue
        graph[a].append(b); indeg[b]+=1
    q=deque([n for n,d in indeg.items() if d==0]); seen=0
    while q:
        n=q.popleft(); seen+=1
        for nxt in graph[n]: indeg[nxt]-=1; q.append(nxt) if indeg[nxt]==0 else None
    if known and seen!=len(known): errors.append("Workflow DAG contains a cycle.")
    for node in nodes:
        if not node.get("node_id") or not node.get("node_type"): errors.append("Each node requires node_id and node_type.")
        if node.get("node_type")=="connector_action" and not node.get("config",{}).get("connector_id"): errors.append(f"Connector node {node.get('node_id')} is missing config.connector_id.")
    return errors
class PersistedDAGScheduler:
    def __init__(self,db:Session,organization_id:str,actor_email="system",actor_role="system"):
        self.db=db; self.organization_id=organization_id; self.actor_email=actor_email; self.actor_role=actor_role
    def _actor_obj(self):
        class A: pass
        a=A(); a.email=self.actor_email; a.role=self.actor_role; a.organization_id=self.organization_id; return a
    def _audit(self,action,target_type,target_id,details=None): self.db.add(AuditLog(organization_id=self.organization_id,actor_email=self.actor_email,actor_role=self.actor_role,action=action,target_type=target_type,target_id=target_id,outcome="success",details=details or {}))
    def create_run(self,template:WorkflowTemplate,input_payload:dict[str,Any],*,simulation_mode=False,idempotency_key=None):
        if idempotency_key:
            existing=self.db.query(WorkflowRun).filter_by(organization_id=self.organization_id,idempotency_key=idempotency_key).first()
            if existing: return existing
        dec=evaluate_policy(self.db,self.organization_id,action="start_workflow",payload={"template_slug":template.slug},actor=self._actor_obj())
        if not dec.allowed: raise PermissionError(dec.reason)
        run=WorkflowRun(organization_id=self.organization_id,template_id=template.id,template_slug=template.slug,input_payload=input_payload,status="created",risk_score=0,current_step=None,logs=[{"event":"workflow_created","policy_decision":dec.dict()}],replay_data={"template_version":template.version,"definition":template.definition_json},simulation_mode=simulation_mode,idempotency_key=idempotency_key)
        self.db.add(run); self.db.commit(); self.db.refresh(run)
        for node in template.definition_json.get("nodes",[]): self.db.add(WorkflowStepRun(workflow_run_id=run.id,node_id=node["node_id"],node_type=node["node_type"],status="pending",input_snapshot={},output_snapshot={},retry_count=0,duration_ms=0))
        self._audit("workflow_started","workflow_run",run.id,{"template_slug":template.slug}); self.db.commit(); self.db.refresh(run); return run
    def run_until_blocked(self,run:WorkflowRun,*,replay_from=None):
        if run.status=="cancelled": return run
        definition=run.replay_data.get("definition") or {}; context={"input":run.input_payload or {}}
        for step in sorted(run.steps,key=lambda s:s.created_at):
            if step.status=="succeeded" and (not replay_from or step.node_id!=replay_from): context[step.node_id]=step.output_snapshot or {}
        run.status="running"; self.db.commit()
        while True:
            ready=self._ready_steps(run,definition,replay_from=replay_from)
            if not ready:
                if any(s.status=="waiting_for_approval" for s in run.steps): run.status="waiting_for_approval"
                elif any(s.status in {"failed","timed_out"} for s in run.steps): run.status="failed"; run.failed_reason="One or more DAG nodes failed."
                elif all(s.status in {"succeeded","skipped"} for s in run.steps): run.status="completed"; run.completed_at=_now()
                else: run.status="partially_completed"
                self.db.commit(); self.db.refresh(run); return run
            step=ready[0]; node=self._node(definition,step.node_id); status=self._execute_step(run,step,node,context); self.db.commit(); self.db.refresh(run); context[step.node_id]=step.output_snapshot or {}
            if status=="waiting_for_approval": run.status="waiting_for_approval"; run.current_step=step.node_id; self.db.commit(); return run
            if status in {"failed","timed_out"} and node.get("failure_policy","fail_run")=="fail_run": run.status="failed"; run.failed_reason=step.error_message or "Node failed"; run.completed_at=_now(); self.db.commit(); return run
    def approve_and_resume(self,approval:ApprovalRequest,approved:bool,reason:str):
        run=approval.workflow_run
        if not run: return None
        if approved:
            for step in run.steps:
                if step.status=="waiting_for_approval": step.status="succeeded"; step.output_snapshot={**(step.output_snapshot or {}),"approval_status":"approved","decision_reason":reason}; step.duration_ms=max(step.duration_ms,1)
            run.logs=(run.logs or [])+[{"event":"approval_approved","reason":reason,"actor":self.actor_email}]; self.db.commit(); self.db.refresh(run); return self.run_until_blocked(run)
        for step in run.steps:
            if step.status=="waiting_for_approval": step.status="failed"; step.error_message="Approval rejected: "+reason
        run.status="failed"; run.failed_reason="Approval rejected: "+reason; run.completed_at=_now(); self.db.commit(); return run
    def replay(self,run,from_node_id=None):
        template=self.db.query(WorkflowTemplate).filter_by(id=run.template_id).first() or self.db.query(WorkflowTemplate).filter_by(organization_id=self.organization_id,slug=run.template_slug).first()
        new=self.create_run(template,{**(run.input_payload or {}),"replayed_from":run.id,"replay_from_node":from_node_id},simulation_mode=True); return self.run_until_blocked(new,replay_from=from_node_id)
    def cancel(self,run,reason="Cancelled by user"):
        if run.status in {"completed","failed","cancelled"}: return run
        run.status="cancelled"; run.failed_reason=reason; run.completed_at=_now(); run.logs=(run.logs or [])+[{"event":"workflow_cancelled","reason":reason}]
        for s in run.steps:
            if s.status in {"pending","queued","running","waiting_for_dependency"}: s.status="cancelled"
        self._audit("workflow_cancelled","workflow_run",run.id,{"reason":reason}); self.db.commit(); self.db.refresh(run); return run
    def _ready_steps(self,run,definition,*,replay_from=None):
        node_map={n["node_id"]:n for n in definition.get("nodes",[])}; steps={s.node_id:s for s in run.steps}; ready=[]
        for step in run.steps:
            if replay_from and step.node_id==replay_from and step.status=="succeeded": step.status="pending"; step.output_snapshot={}; self.db.flush()
            if step.status!="pending": continue
            deps=node_map.get(step.node_id,{}).get("depends_on") or []; deps += [e.get("from") for e in definition.get("edges",[]) if e.get("to")==step.node_id and e.get("from")]; deps=list(dict.fromkeys(deps))
            if all(steps[d].status in {"succeeded","skipped"} for d in deps if d in steps): ready.append(step)
            elif deps: step.output_snapshot={"waiting_on":[d for d in deps if d in steps and steps[d].status not in {"succeeded","skipped"}]}
        return ready
    def _execute_step(self,run,step,node,context):
        started=perf_counter(); step.status="running"; run.current_step=step.node_id; step.input_snapshot={"context_keys":list(context.keys()),"run_input":run.input_payload}; self._audit("workflow_node_started","workflow_step",step.id,{"node_id":step.node_id,"node_type":step.node_type,"workflow_run_id":run.id})
        try:
            output,status=self._node_logic(run,node,context); step.output_snapshot=output; step.status=status
            if status=="waiting_for_approval": self._ensure_approval(run,step,output); self._audit("approval_requested","workflow_run",run.id,output)
            else: self._audit("workflow_node_completed","workflow_step",step.id,{"node_id":step.node_id,"status":status,"workflow_run_id":run.id})
        except Exception as exc:
            step.retry_count+=1; limit=int(node.get("retry_limit",1))
            if step.retry_count<=limit: step.status="pending"; step.error_message=f"Retry scheduled after error: {exc}"
            else: step.status="failed"; step.error_message=str(exc); self._audit("workflow_node_failed","workflow_step",step.id,{"node_id":step.node_id,"error":str(exc),"workflow_run_id":run.id})
        step.duration_ms=max(1,int((perf_counter()-started)*1000)); run.logs=(run.logs or [])+[{"ts":_now().isoformat(),"event":"node_state","node_id":step.node_id,"status":step.status,"duration_ms":step.duration_ms}]; return step.status
    def _node_logic(self,run,node,context):
        t=node.get("node_type"); payload=context.get("input",{}); text=payload.get("text") or payload.get("body") or payload.get("document_text") or ""
        if t=="ingest_document": return {"text":redact_text(text),"filename":payload.get("filename","synthetic_input.txt"),"prompt_injection_findings":detect_prompt_injection(text)},"succeeded"
        if t=="classify_document": return classify_document((context.get("ingest") or {}).get("text",text)).__dict__,"succeeded"
        if t=="extract_fields":
            source=(context.get("ingest") or {}).get("text",text); fields=extract_key_values(source); doc_type=(context.get("classify") or {}).get("document_type","general_business_document"); required={"invoice":["vendor","invoice_number","total","due_date"],"rfp":["deadline","mandatory_documents"],"support_attachment":["support_risk_terms"],"policy_document":["control_id","evidence"]}.get(doc_type,[]); return {"document_type":doc_type,"fields":fields,"confidence":confidence_score(fields,required),"required_fields":required},"succeeded"
        if t=="validate_fields":
            ex=context.get("extract",{}); fields=ex.get("fields",{}); missing=[f for f in ex.get("required_fields",[]) if not fields.get(f)]; return {"valid":not missing,"missing_fields":missing,"po_mismatch":False,"duplicate_invoice":bool(payload.get("duplicate_invoice") or "duplicate" in text.lower())},"succeeded"
        if t=="score_risk":
            findings=(context.get("ingest") or {}).get("prompt_injection_findings",[]); valid=(context.get("validate") or {}).get("valid",True); confidence=float((context.get("extract") or {}).get("confidence",1)); fields=(context.get("extract") or {}).get("fields",{}); score=10+(45 if findings else 0)+(25 if not valid else 0)+max(0,(1-confidence)*30); low=text.lower(); score += 15 if any(k in low for k in ["payment","refund","legal","vip","vendor bank","angry","urgent","complaint"]) else 0; score += 20 if fields.get("support_risk_terms") else 0; amount=float(fields.get("total") or payload.get("amount") or 0); dec=evaluate_policy(self.db,self.organization_id,actor=self._actor_obj(),action="workflow_node",payload={"risk_score":score,"amount":amount,"confidence":confidence,"prompt_injection_detected":bool(findings)}); run.risk_score=round(min(score,100),2); return {"risk_score":run.risk_score,"risk_level":dec.risk_level,"policy_decision":dec.dict(),"amount":amount},"succeeded"
        if t=="create_task":
            dept={"invoice_approval":"Finance","rfp_response":"Sales","support_escalation":"Support","compliance_evidence":"Security"}.get(run.template_slug,"Operations"); task=Task(organization_id=self.organization_id,workflow_run_id=run.id,title=f"Review {run.template_slug} output",department=dept,assignee_email="reviewer@example.com",priority="high" if run.risk_score>=60 else "normal",metadata_json={"node_id":node.get("node_id")}); self.db.add(task); self.db.flush(); return {"task_id":task.id,"department":dept,"status":"open"},"succeeded"
        if t=="request_approval":
            cfg=node.get("config",{}); threshold=float(cfg.get("risk_threshold",60)); amount_threshold=float(cfg.get("amount_threshold",1000)); amount=float((context.get("risk") or {}).get("amount") or 0); needed=run.risk_score>=threshold or amount>amount_threshold or node.get("requires_approval",False)
            if needed and not run.simulation_mode: return {"approval_required":True,"reason":"Risk, amount, or connector action requires human approval.","risk_score":run.risk_score},"waiting_for_approval"
            return {"approval_required":needed,"auto_continued":True,"simulation_mode":run.simulation_mode},"succeeded"
        if t=="generate_draft": return {"draft":"Synthetic reply draft generated for human review.","send_status":"not_sent"},"succeeded"
        if t=="connector_action":
            from app.connectors.registry import get_connector
            cfg=node.get("config",{}); connector_id=cfg.get("connector_id","file_demo"); action=cfg.get("action","write_file"); result=get_connector(connector_id).execute(self.db,self.organization_id,action,{"run_id":run.id,**payload},dry_run=run.simulation_mode); return {"connector_result":result.__dict__},"succeeded"
        if t in {"export_report","generate_report"}:
            data=build_report_payload(run.template_slug,{"workflow_run_id":run.id,"risk_score":run.risk_score,"input":payload,"synthetic":True}); report=Report(organization_id=self.organization_id,workflow_run_id=run.id,title=data.get("title","Workflow Report"),report_type=run.template_slug,summary=data.get("executive_summary","Synthetic demo report"),data=data,paths={}); self.db.add(report); self.db.flush(); return {"report_id":report.id,"title":report.title},"succeeded"
        if t=="branch": return {"branch":"high_risk" if run.risk_score>=45 else "standard","risk_score":run.risk_score},"succeeded"
        if t=="merge": return {"merged":True},"succeeded"
        if t=="wait_for_human": return {"waiting":True},"waiting_for_approval"
        if t=="stop": return {"closed":True},"succeeded"
        return {"note":f"No-op node type {t}"},"succeeded"
    def _node(self,definition,node_id): return next(n for n in definition.get("nodes",[]) if n.get("node_id")==node_id)
    def _ensure_approval(self,run,step,output):
        if not self.db.query(ApprovalRequest).filter_by(workflow_run_id=run.id,status="pending").first(): self.db.add(ApprovalRequest(organization_id=self.organization_id,workflow_run_id=run.id,title=f"Approve {run.template_slug} node {step.node_id}",reason=output.get("reason","Human approval required."),status="pending",risk_score=run.risk_score,requested_by=self.actor_email,reviewer_role="reviewer",payload={"workflow_run_id":run.id,"node_id":step.node_id,"risk_score":run.risk_score}))
