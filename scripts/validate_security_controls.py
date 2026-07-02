from _validation_utils import write_result, ensure
from fastapi.testclient import TestClient
from app.main import app
from app.db.session import init_db, SessionLocal
from app.db.seed import seed_database
def login(c,e,p):
    r=c.post('/auth/login',json={'email':e,'password':p}); ensure(r.status_code==200,r.text); return {'Authorization':'Bearer '+r.json()['access_token']}
def main():
    init_db(drop_existing=True); db=SessionLocal(); seed_database(db); db.close(); c=TestClient(app); viewer=login(c,'viewer@example.com','viewer123'); admin=login(c,'admin@example.com','admin123'); approvals=c.get('/approvals',headers=admin).json(); denied=c.post(f"/approvals/{approvals[0]['id']}/approve",headers=viewer,json={'reason':'no'}); invalid=c.post('/documents/upload',headers=admin,files={'file':('x.exe',b'bad','application/octet-stream')}); webhook=c.post('/connectors/webhook_demo/actions/post_json/dry-run',headers=admin,json={'payload':{'url':'http://169.254.169.254/latest'}}); logs=c.get('/audit-logs',headers=admin).json(); ensure(denied.status_code==403,'viewer not denied'); ensure(invalid.status_code in {400,415},'invalid upload not rejected'); ensure(webhook.status_code==200,'dry-run crashed'); ensure(any(l['outcome']=='denied' for l in logs),'denied audit missing'); write_result('security_controls_validation',{'passed':True,'viewer_approval_status':denied.status_code,'invalid_upload_status':invalid.status_code,'audit_events':len(logs)})
if __name__=='__main__': main()
