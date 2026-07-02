
from __future__ import annotations
from app.connectors.base import AccountingDemoConnector, BaseConnector, CRMDemoConnector, EmailDemoConnector, FileDemoConnector, SheetsDemoConnector, SlackDemoConnector, WebhookDemoConnector
_CONNECTORS={c.connector_id:c for c in [EmailDemoConnector(),SlackDemoConnector(),SheetsDemoConnector(),CRMDemoConnector(),AccountingDemoConnector(),WebhookDemoConnector(),FileDemoConnector()]}
def list_connectors(): return list(_CONNECTORS.values())
def get_connector(connector_id:str)->BaseConnector: return _CONNECTORS[connector_id]
