from _validation_utils import write_result, ensure
from app.db.session import init_db, SessionLocal
from app.db.seed import seed_database
from app.db.models import WorkflowTemplate
from app.workflows.dag import PersistedDAGScheduler, validate_dag
def main():
    init_db(drop_existing=True); db=SessionLocal(); seed_database(db)
    tpl=db.query(WorkflowTemplate).filter_by(slug='invoice_approval').first(); ensure(tpl is not None,'template missing'); ensure(not validate_dag(tpl.definition_json),'dag invalid')
    sched=PersistedDAGScheduler(db,tpl.organization_id,'admin@example.com','admin'); run=sched.create_run(tpl,{'text':'Invoice Number: INV-DAG\nVendor: Acme Supplies\nTotal: USD 5000\nDue Date: 2026-08-01\nPayment requested','action_type':'payment_export'}); run=sched.run_until_blocked(run)
    ensure(run.status=='waiting_for_approval',f'expected approval pause got {run.status}')
    write_result('dag_scheduler_validation', {'passed':True,'run_id':run.id,'status':run.status,'steps':[{'node_id':s.node_id,'status':s.status} for s in run.steps]}); db.close()
if __name__=='__main__': main()
