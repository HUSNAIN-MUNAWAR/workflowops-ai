from fastapi.testclient import TestClient
from app.db.session import init_db, SessionLocal
from app.db.seed import seed_database
from app.db.models import WorkflowTemplate
from app.main import app
from app.workflows.dag import validate_dag

def _setup():
    init_db(drop_existing=True); db=SessionLocal(); seed_database(db); db.close(); client=TestClient(app)
    def login(email,pw):
        r=client.post('/auth/login',json={'email':email,'password':pw}); assert r.status_code==200,r.text; return {'Authorization':'Bearer '+r.json()['access_token']}
    return client,login('admin@example.com','admin123'),login('manager@example.com','manager123'),login('reviewer@example.com','reviewer123'),login('viewer@example.com','viewer123')

def test_persisted_dag_pause_resume():
    client,admin,_m,reviewer,_v=_setup()
    r=client.post('/workflow-runs',headers=admin,json={'template_slug':'invoice_approval','input_payload':{'text':'Invoice Number: INV-DAG\nVendor: Acme Supplies\nTotal: USD 9000\nDue Date: 2026-08-22','action_type':'payment_export'}})
    assert r.status_code==200,r.text; run=r.json(); assert run['status']=='waiting_for_approval'
    assert any(s['status']=='waiting_for_approval' for s in client.get(f"/workflow-runs/{run['id']}/timeline",headers=admin).json())
    approval=[a for a in client.get('/approvals',headers=reviewer).json() if a['status']=='pending'][0]
    assert client.post(f"/approvals/{approval['id']}/approve",headers=reviewer,json={'reason':'ok'}).status_code==200

def test_queue_connectors_policy_builder_security():
    client,admin,_m,_r,viewer=_setup()
    run=client.post('/workflow-runs',headers=admin,json={'template_slug':'support_escalation','input_payload':{'text':'VIP angry legal refund urgent'}}).json()
    assert client.post(f"/workflow-runs/{run['id']}/enqueue",headers=admin).status_code==200
    assert 'counts' in client.get('/queue/status',headers=admin).json()
    assert len(client.get('/connectors',headers=admin).json())>=7
    assert client.post('/connectors/email_demo/actions/create_draft/dry-run',headers=admin,json={'payload':{'to':'client@example.com'}}).status_code==200
    assert client.post('/connectors/accounting_demo/actions/export_invoice/execute',headers=admin,json={'payload':{'invoice_number':'INV-X'}}).status_code==409
    dec=client.post('/policies/evaluate',headers=admin,json={'action':'start_workflow','payload':{'template_slug':'invoice_approval','invoice_amount':5000}}).json(); assert dec['requires_approval'] is True
    assert client.put('/policies/default',headers=viewer,json={'risk_review_threshold':95}).status_code==403
    assert client.post('/documents/upload',headers=admin,files={'file':('x.exe',b'bad','application/octet-stream')}).status_code==400

def test_builder_validation_clone_publish_and_invalid_token():
    client,admin,*_=_setup()
    bad={'nodes':[{'node_id':'a','node_type':'branch'},{'node_id':'b','node_type':'merge'}],'edges':[{'from':'a','to':'b'},{'from':'b','to':'a'}]}
    assert client.post('/workflow-builder/validate',headers=admin,json={'definition_json':bad}).json()['valid'] is False
    db=SessionLocal(); tpl=db.query(WorkflowTemplate).filter_by(slug='invoice_approval').first(); tid=tpl.id; db.close()
    clone=client.post(f'/workflow-builder/templates/{tid}/clone',headers=admin); assert clone.status_code==200, clone.text
    assert client.post(f"/workflow-builder/templates/{clone.json()['id']}/publish",headers=admin).status_code==200
    assert client.get('/dashboard/summary',headers={'Authorization':'Bearer invalid'}).status_code==401

def test_validate_dag_missing_node_detected():
    assert validate_dag({'nodes':[{'node_id':'a','node_type':'ingest_document'}],'edges':[{'from':'a','to':'missing'}]})

def test_app_lifespan_startup_exposes_health():
    init_db(drop_existing=True)
    with TestClient(app) as client:
        response = client.get('/health')
    assert response.status_code == 200
    assert response.json() == {'status': 'ok'}
