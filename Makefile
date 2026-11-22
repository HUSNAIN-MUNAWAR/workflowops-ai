
.PHONY: help install setup db-upgrade db-downgrade db-reset seed demo-reset test validate animation runtime-evidence dev worker docker-up docker-down docker-logs docker-config reports screenshots screenshots-live frontend-check backend-check e2e clean
help:
	@echo "WorkflowOps AI commands: install, db-upgrade, seed, dev, worker, test, validate, frontend-check, e2e, reports, screenshots, docker-up"
install setup:
	python -m pip install -r backend/requirements.txt
	cd frontend && npm install --no-audit --no-fund
backend-check:
	PYTHONPATH=backend python -m compileall -q backend/app scripts
db-upgrade:
	cd backend && PYTHONPATH=. alembic upgrade head
db-downgrade:
	cd backend && PYTHONPATH=. alembic downgrade -1
db-reset:
	rm -f backend/workflowops.db workflowops.db
	$(MAKE) db-upgrade
demo-reset: db-reset seed reports
seed:
	PYTHONPATH=backend python scripts/seed_demo_data.py
test: backend-check
	PYTHONPATH=backend pytest -q backend/tests
validate:
	PYTHONPATH=backend python scripts/validate_dag_scheduler.py
	PYTHONPATH=backend python scripts/validate_background_worker.py
	PYTHONPATH=backend python scripts/validate_connectors.py
	PYTHONPATH=backend python scripts/validate_policy_engine.py
	PYTHONPATH=backend python scripts/validate_invoice_workflow.py
	PYTHONPATH=backend python scripts/validate_rfp_workflow.py
	PYTHONPATH=backend python scripts/validate_support_workflow.py
	PYTHONPATH=backend python scripts/validate_reliability_tests.py
	PYTHONPATH=backend python scripts/validate_security_controls.py
	PYTHONPATH=backend python scripts/validate_document_extraction.py
animation:
	PYTHONPATH=backend python scripts/generate_workflow_animation.py
runtime-evidence:
	PYTHONPATH=backend python scripts/generate_real_runtime_video.py
reports:
	PYTHONPATH=backend python scripts/generate_demo_reports.py
screenshots:
	PYTHONPATH=backend python scripts/capture_real_screenshots.py
screenshots-live:
	cd frontend && npm run screenshots:readme
frontend-check:
	cd frontend && npm run typecheck && npm run build
e2e:
	cd frontend && npm run e2e
dev:
	PYTHONPATH=backend uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
worker:
	PYTHONPATH=backend python -m app.worker
docker-config:
	docker compose config >/dev/null
docker-up:
	docker compose up --build
docker-down:
	docker compose down -v
docker-logs:
	docker compose logs -f --tail=200
clean:
	rm -rf frontend/.next frontend/node_modules frontend/tsconfig.tsbuildinfo .pytest_cache
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
