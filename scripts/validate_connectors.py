from _validation_utils import write_result, ensure
from app.db.session import init_db, SessionLocal
from app.db.seed import seed_database
from app.connectors.registry import list_connectors, get_connector
def main():
    init_db(drop_existing=True); db=SessionLocal(); seed_database(db); org='demo-org'; cons=[c.connector_id for c in list_connectors()]; ensure(len(cons)>=7,'expected seven connectors'); dry=get_connector('email_demo').execute(db,org,'create_draft',{'to':'client@example.com'},dry_run=True); real=get_connector('sheets_demo').execute(db,org,'append_row',{'row':{'invoice':'INV-1'}},dry_run=False); blocked=get_connector('webhook_demo').execute(db,org,'post_json',{'url':'http://169.254.169.254/latest'},dry_run=False); ensure(blocked.status=='blocked','ssrf guard missing'); write_result('connectors_validation',{'passed':True,'connectors':cons,'dry_run':dry.__dict__,'local_write':real.__dict__,'blocked':blocked.__dict__}); db.close()
if __name__=='__main__': main()
