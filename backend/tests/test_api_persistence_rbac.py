from fastapi.testclient import TestClient
from app.db.session import init_db, SessionLocal
from app.db.seed import seed_database
from app.main import app


def _client_and_tokens():
    init_db(drop_existing=True)
    db = SessionLocal()
    try:
        seed_database(db, reset=False)
    finally:
        db.close()
    client = TestClient(app)
    def login(email, password):
        r = client.post('/auth/login', json={'email': email, 'password': password})
        assert r.status_code == 200, r.text
        return {'Authorization': 'Bearer ' + r.json()['access_token']}
    return client, login('admin@example.com','admin123'), login('reviewer@example.com','reviewer123'), login('viewer@example.com','viewer123')


def test_dashboard_templates_workflow_and_approval_api_paths():
    client, admin, reviewer, _viewer = _client_and_tokens()
    assert client.get('/dashboard/summary', headers=admin).status_code == 200
    templates = client.get('/workflow-templates', headers=admin).json()
    assert any(t['slug'] == 'invoice_approval' for t in templates)
    run = client.post('/workflow-runs', headers=admin, json={'template_slug':'invoice_approval','input_payload':{'text':'Invoice Number: INV-API\nVendor: Acme\nTotal: USD 7000\nDue Date: 2026-08-01','action_type':'payment_export'}})
    assert run.status_code == 200, run.text
    run_id = run.json()['id']
    assert client.get(f'/workflow-runs/{run_id}/timeline', headers=admin).status_code == 200
    approvals = client.get('/approvals', headers=reviewer).json()
    pending = [a for a in approvals if a['status'] == 'pending']
    assert pending
    decision = client.post(f"/approvals/{pending[0]['id']}/approve", headers=reviewer, json={'reason':'API test approval'})
    assert decision.status_code == 200, decision.text
    assert decision.json()['status'] == 'approved'


def test_viewer_cannot_approve_and_denied_action_is_audited():
    client, admin, _reviewer, viewer = _client_and_tokens()
    approvals = client.get('/approvals', headers=admin).json()
    r = client.post(f"/approvals/{approvals[0]['id']}/approve", headers=viewer, json={'reason':'should fail'})
    assert r.status_code == 403
    logs = client.get('/audit-logs', headers=admin).json()
    assert any(log['outcome'] == 'denied' and 'approval:decide' in log['action'] for log in logs)


def test_health_ready_metrics():
    client, admin, *_ = _client_and_tokens()
    assert client.get('/health').json()['status'] == 'ok'
    assert client.get('/ready').json()['status'] == 'ready'
    metrics = client.get('/metrics').text
    assert 'workflow_runs_total' in metrics
