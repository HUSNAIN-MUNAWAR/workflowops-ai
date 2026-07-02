from _validation_utils import write_result, ensure
from app.db.session import init_db, SessionLocal
from app.db.seed import seed_database
from app.db.models import WorkflowTemplate
from app.workflows.dag import PersistedDAGScheduler
from app.queueing import enqueue_workflow_run, queue_status
def main():
    init_db(drop_existing=True); db=SessionLocal(); seed_database(db); tpl=db.query(WorkflowTemplate).filter_by(slug='support_escalation').first(); run=PersistedDAGScheduler(db,tpl.organization_id,'admin@example.com','admin').create_run(tpl,{'text':'VIP customer is angry and asks for refund legal complaint risk'},simulation_mode=True); job=enqueue_workflow_run(db,run); status=queue_status(db); ensure(job.status in {'completed','failed'},f'bad job status {job.status}'); ensure(status['counts']['completed']+status['counts']['failed']>=1,'queue metrics missing'); write_result('background_worker_validation',{'passed':True,'job_id':job.id,'job_status':job.status,'queue':status}); db.close()
if __name__=='__main__': main()
