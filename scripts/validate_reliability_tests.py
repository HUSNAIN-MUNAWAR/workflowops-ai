from _validation_utils import save_validation, fresh_db
from app.modules.reliability.evalbench import run_reliability_suite

def main():
    db=fresh_db()
    suite=run_reliability_suite()
    if suite['scenario_count'] < 12: raise SystemExit('Expected at least 12 reliability cases')
    if suite['failed_count'] < 2: raise SystemExit('Expected intentional demo gaps to be reported')
    save_validation('reliability_tests_validation', {'status':'passed','scenario_count':suite['scenario_count'],'passed_count':suite['passed_count'],'failed_count':suite['failed_count'],'reliability_score':suite['reliability_score'],'safety_score':suite['safety_score'],'intentional_demo_gaps':[c['scenario_type'] for c in suite['failed_cases']]})
if __name__=='__main__': main()
