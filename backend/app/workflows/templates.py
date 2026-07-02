
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any
@dataclass
class WorkflowNode:
    node_id: str; node_type: str; name: str; config: dict[str, Any]=field(default_factory=dict); retry_limit:int=1; requires_approval:bool=False; depends_on:list[str]=field(default_factory=list); timeout_seconds:int=30; failure_policy:str="fail_run"
@dataclass
class WorkflowTemplate:
    slug:str; name:str; description:str; nodes:list[WorkflowNode]; risk_threshold:float=65.0; version:str="3.0.0"; edges:list[dict[str,Any]]=field(default_factory=list)
    def as_definition(self):
        edges=self.edges or [{"from":a.node_id,"to":b.node_id,"condition":"success"} for a,b in zip(self.nodes,self.nodes[1:])]
        return {"slug":self.slug,"version":self.version,"risk_threshold":self.risk_threshold,"nodes":[n.__dict__ for n in self.nodes],"edges":edges,"entrypoint":self.nodes[0].node_id if self.nodes else None,"safety":{"approval_required_for_external_actions":True}}
def n(node_id,node_type,name,config=None,retry=1,approve=False,deps=None,timeout=30,failure="fail_run"):
    return WorkflowNode(node_id,node_type,name,config or {},retry,approve,deps or [],timeout,failure)
def invoice_template():
    nodes=[n("ingest","ingest_document","Ingest invoice"),n("classify","classify_document","Classify",deps=["ingest"]),n("extract","extract_fields","Extract",deps=["classify"]),n("validate","validate_fields","Validate",deps=["extract"]),n("risk","score_risk","Risk",deps=["validate"]),n("approval","request_approval","Finance approval",{"risk_threshold":60,"amount_threshold":1000},True,["risk"]),n("export","connector_action","Accounting export draft",{"connector_id":"accounting_demo","action":"export_invoice","approval_required":True},deps=["approval"]),n("report","export_report","Report",deps=["export"]),n("stop","stop","Close",deps=["report"])]
    return WorkflowTemplate("invoice_approval","Invoice-to-Payment Approval","DAG workflow for invoice extraction, policy review, human approval and safe local accounting export draft.",nodes,60)
def email_task_template():
    return WorkflowTemplate("email_to_task","Email Inbox-to-Task","Classify emails, create tasks, draft replies and approval gate outbound actions.",[n("ingest","ingest_document","Ingest email"),n("classify","classify_document","Classify",deps=["ingest"]),n("extract","extract_fields","Extract",deps=["classify"]),n("risk","score_risk","Risk",deps=["extract"]),n("task","create_task","Create task",deps=["risk"]),n("draft","generate_draft","Draft",deps=["task"]),n("approval","request_approval","Approve draft",{"risk_threshold":55},True,["draft"]),n("notify","connector_action","Store draft",{"connector_id":"email_demo","action":"create_draft","approval_required":True},deps=["approval"]),n("report","export_report","Report",deps=["notify"]),n("stop","stop","Close",deps=["report"])],55)
def rfp_template():
    return WorkflowTemplate("rfp_response","RFP / Proposal Automation","Extract requirements, build compliance matrix and approval checklist.",[n("ingest","ingest_document","Ingest RFP"),n("classify","classify_document","Classify",deps=["ingest"]),n("extract","extract_fields","Extract requirements",deps=["classify"]),n("validate","validate_fields","Validate",deps=["extract"]),n("risk","score_risk","Bid risk",deps=["validate"]),n("task","create_task","Assign proposal tasks",deps=["risk"]),n("matrix","export_report","Compliance matrix",deps=["task"]),n("approval","request_approval","Bid approval",{"risk_threshold":65},True,["matrix"]),n("stop","stop","Close",deps=["approval"])],65)
def compliance_template():
    return WorkflowTemplate("compliance_evidence","Compliance Evidence Automation","Map synthetic controls to evidence and generate pack.",[n("ingest","ingest_document","Ingest evidence"),n("classify","classify_document","Classify",deps=["ingest"]),n("extract","extract_fields","Map controls",deps=["classify"]),n("risk","score_risk","Coverage risk",deps=["extract"]),n("task","create_task","Missing evidence tasks",deps=["risk"]),n("report","export_report","Evidence pack",deps=["task"]),n("stop","stop","Close",deps=["report"])],50)
def support_template():
    return WorkflowTemplate("support_escalation","Customer Support Escalation","Detect refund/legal/VIP anger signals and approval-gate sensitive response.",[n("ingest","ingest_document","Ingest ticket"),n("classify","classify_document","Classify",deps=["ingest"]),n("extract","extract_fields","Extract risk terms",deps=["classify"]),n("risk","score_risk","Escalation risk",deps=["extract"]),n("branch","branch","Route",deps=["risk"]),n("task","create_task","Support task",deps=["branch"]),n("draft","generate_draft","Draft reply",deps=["task"]),n("approval","request_approval","Approve response",{"risk_threshold":45},True,["draft"]),n("notify","connector_action","Local notification",{"connector_id":"slack_demo","action":"post_message","approval_required":True},deps=["approval"]),n("report","export_report","Report",deps=["notify"]),n("stop","stop","Close",deps=["report"])],45)
def reliability_template():
    return WorkflowTemplate("workflow_reliability","AI Workflow Reliability Tester","Runs synthetic red-team workflow reliability scenarios.",[n("scenario","generate_test_scenarios","Generate scenarios"),n("simulate","simulate_workflow","Simulate",deps=["scenario"]),n("detect","detect_failures","Detect",deps=["simulate"]),n("replay","build_replay","Replay",deps=["detect"]),n("report","export_report","Report",deps=["replay"])],40)
def load_builtin_templates(): return [invoice_template(),email_task_template(),rfp_template(),compliance_template(),support_template(),reliability_template()]
def template_by_slug(slug):
    for t in load_builtin_templates():
        if t.slug==slug: return t
    raise KeyError(slug)
