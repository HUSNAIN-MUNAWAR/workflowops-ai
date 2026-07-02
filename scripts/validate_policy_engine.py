from _validation_utils import write_result, ensure
from app.db.session import init_db, SessionLocal
from app.db.seed import seed_database
from app.db.models import User
from app.policies.engine import evaluate_policy
def main():
    init_db(drop_existing=True); db=SessionLocal(); seed_database(db); user=db.query(User).filter_by(email='admin@example.com').first(); approval=evaluate_policy(db,user.organization_id,actor=user,action='workflow_node',payload={'amount':5000,'risk_score':20,'confidence':.95}); block=evaluate_policy(db,user.organization_id,actor=user,action='workflow_node',payload={'prompt_injection_detected':True,'risk_score':80}); ensure(approval.requires_approval,'amount threshold missing'); ensure(not block.allowed,'prompt injection not blocked'); write_result('policy_engine_validation',{'passed':True,'approval_decision':approval.dict(),'block_decision':block.dict()}); db.close()
if __name__=='__main__': main()
