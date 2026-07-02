
from __future__ import annotations
from dataclasses import dataclass
from typing import Any
from pathlib import Path
from sqlalchemy.orm import Session
from app.db.models import DemoAccountingExport, DemoCRMRecord, DemoEmailDraft, DemoFileObject, DemoNotification, DemoSheetRow
@dataclass
class ConnectorActionSchema:
    name:str; description:str; high_risk:bool=True; approval_required:bool=True
@dataclass
class ConnectorResult:
    connector_id:str; action_name:str; status:str; dry_run:bool; message:str; data:dict[str,Any]
class BaseConnector:
    connector_id="base"; name="Base"; category="demo"; description=""; actions:dict[str,ConnectorActionSchema]={}
    def list_actions(self): return list(self.actions.values())
    def execute(self,db:Session,organization_id:str,action_name:str,payload:dict[str,Any],*,dry_run:bool=True,idempotency_key:str|None=None)->ConnectorResult:
        if action_name not in self.actions: raise ValueError(f"Unsupported connector action: {action_name}")
        if dry_run: return ConnectorResult(self.connector_id,action_name,"dry_run_ok",True,"Dry run passed. No external action executed.",{"payload_preview":payload})
        return self._execute(db,organization_id,action_name,payload,idempotency_key)
    def _execute(self,db,organization_id,action_name,payload,idempotency_key): raise NotImplementedError
class EmailDemoConnector(BaseConnector):
    connector_id="email_demo"; name="Email Draft Connector"; category="email"; description="Writes draft emails to the local database. Never sends real email."; actions={"create_draft":ConnectorActionSchema("create_draft","Create local draft email",True,True)}
    def _execute(self,db,org,action,payload,key):
        row=DemoEmailDraft(organization_id=org,to_email=payload.get("to","client@example.com"),subject=payload.get("subject","WorkflowOps draft"),body=payload.get("body","Synthetic draft")); db.add(row); db.commit(); db.refresh(row); return ConnectorResult(self.connector_id,action,"draft_created",False,"Local email draft stored; no email sent.",{"draft_id":row.id})
class SlackDemoConnector(BaseConnector):
    connector_id="slack_demo"; name="Slack-style Notification Connector"; category="messaging"; description="Stores notification rows locally."; actions={"post_message":ConnectorActionSchema("post_message","Store notification",True,True)}
    def _execute(self,db,org,action,payload,key):
        row=DemoNotification(organization_id=org,channel=payload.get("channel","demo-support"),message=payload.get("message","Synthetic notification")); db.add(row); db.commit(); db.refresh(row); return ConnectorResult(self.connector_id,action,"notification_stored",False,"Local notification stored.",{"notification_id":row.id})
class SheetsDemoConnector(BaseConnector):
    connector_id="sheets_demo"; name="Google Sheets-style Connector"; category="spreadsheet"; description="Appends local demo rows."; actions={"append_row":ConnectorActionSchema("append_row","Append local row",False,False)}
    def _execute(self,db,org,action,payload,key):
        row=DemoSheetRow(organization_id=org,sheet_name=payload.get("sheet_name","workflowops_demo"),row_data=payload.get("row",payload)); db.add(row); db.commit(); db.refresh(row); return ConnectorResult(self.connector_id,action,"row_appended",False,"Local sheet row stored.",{"row_id":row.id})
class CRMDemoConnector(BaseConnector):
    connector_id="crm_demo"; name="CRM-style Connector"; category="crm"; description="Creates local CRM records."; actions={"create_task":ConnectorActionSchema("create_task","Create local CRM task",False,False),"create_lead":ConnectorActionSchema("create_lead","Create local CRM lead",False,False)}
    def _execute(self,db,org,action,payload,key):
        row=DemoCRMRecord(organization_id=org,record_type=action.replace('create_',''),record_data=payload); db.add(row); db.commit(); db.refresh(row); return ConnectorResult(self.connector_id,action,"crm_record_created",False,"Local CRM record stored.",{"record_id":row.id})
class AccountingDemoConnector(BaseConnector):
    connector_id="accounting_demo"; name="Accounting Export Connector"; category="accounting"; description="Writes local accounting export rows; no payments are executed."; actions={"export_invoice":ConnectorActionSchema("export_invoice","Create local invoice export",True,True)}
    def _execute(self,db,org,action,payload,key):
        row=DemoAccountingExport(organization_id=org,export_type="invoice",export_data=payload); db.add(row); db.commit(); db.refresh(row); return ConnectorResult(self.connector_id,action,"invoice_export_stored",False,"Local accounting export stored. No payment executed.",{"export_id":row.id})
class WebhookDemoConnector(BaseConnector):
    connector_id="webhook_demo"; name="Webhook Demo Connector"; category="webhook"; description="Localhost-only demo webhook guard."; actions={"post_json":ConnectorActionSchema("post_json","Simulate JSON webhook",True,True)}
    def _execute(self,db,org,action,payload,key):
        url=payload.get("url","")
        if not (url.startswith("http://localhost") or url.startswith("http://127.0.0.1")): return ConnectorResult(self.connector_id,action,"blocked",False,"Webhook URL blocked by localhost-only SSRF guard in demo mode.",{"url":url})
        return ConnectorResult(self.connector_id,action,"local_webhook_simulated",False,"Localhost webhook simulated; no external network call made.",{"url":url})
class FileDemoConnector(BaseConnector):
    connector_id="file_demo"; name="File Storage Demo Connector"; category="file_storage"; description="Writes files under sample_outputs/demo_storage."; actions={"write_file":ConnectorActionSchema("write_file","Write local demo file",False,False)}
    def _execute(self,db,org,action,payload,key):
        out=Path("sample_outputs/demo_storage"); out.mkdir(parents=True,exist_ok=True); filename=Path(payload.get("filename","workflowops_output.txt")).name; path=out/filename; path.write_text(str(payload.get("content","Synthetic demo file")),encoding="utf-8"); row=DemoFileObject(organization_id=org,filename=filename,storage_path=str(path),metadata_json={"idempotency_key":key}); db.add(row); db.commit(); db.refresh(row); return ConnectorResult(self.connector_id,action,"file_written",False,"Local file stored.",{"file_id":row.id,"path":str(path)})
