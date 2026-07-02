from __future__ import annotations
import time
from app.core.config import get_settings
from app.db.session import SessionLocal
from app.db.models import QueueJob
from app.queueing import execute_job_sync
def run_local_worker_loop(poll_seconds: float = 2.0) -> None:
    print('WorkflowOps local DB worker started. Ctrl+C to stop.')
    while True:
        db=SessionLocal()
        try:
            job=db.query(QueueJob).filter_by(status='queued').order_by(QueueJob.created_at).first()
            if job: execute_job_sync(db,job.id)
        finally: db.close()
        time.sleep(poll_seconds)
def main():
    settings=get_settings()
    if settings.local_sync_worker: run_local_worker_loop()
    else:
        from redis import Redis
        from rq import Worker, Queue
        conn=Redis.from_url(settings.redis_url)
        Worker([Queue('workflowops',connection=conn)],connection=conn).work()
if __name__=='__main__': main()
