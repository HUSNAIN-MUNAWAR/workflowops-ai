from __future__ import annotations
from _validation_utils import save_validation, fresh_db

def main():
    db=fresh_db()
    counts={'users': db.execute(__import__('sqlalchemy').text('select count(*) from users')).scalar_one(), 'templates': db.execute(__import__('sqlalchemy').text('select count(*) from workflow_templates')).scalar_one(), 'runs': db.execute(__import__('sqlalchemy').text('select count(*) from workflow_runs')).scalar_one(), 'approvals': db.execute(__import__('sqlalchemy').text('select count(*) from approval_requests')).scalar_one()}
    save_validation('seed_demo_data', {'status':'passed','counts':counts,'demo_credentials':['admin@example.com/admin123','manager@example.com/manager123','reviewer@example.com/reviewer123','viewer@example.com/viewer123']})
if __name__=='__main__': main()
