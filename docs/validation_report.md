# Validation Report

Final sandbox validation:

- Backend tests: 18 passed, 3 warnings.
- Alembic SQLite migration: passed.
- OpenAPI: 52 paths returned from `/openapi.json`.
- Health/readiness/metrics endpoints returned 200.
- Frontend typecheck: passed.
- Frontend build: passed, 23 static routes generated.
- Report generation: six report families generated in JSON, Markdown, HTML, and PDF.
- PDF render check: workflow reliability report PDF rendered to PNG successfully.
- Final validation scripts passed individually:
  - validate_dag_scheduler.py
  - validate_background_worker.py
  - validate_connectors.py
  - validate_policy_engine.py
  - validate_invoice_workflow.py
  - validate_rfp_workflow.py
  - validate_support_workflow.py
  - validate_reliability_tests.py
  - validate_document_extraction.py
  - validate_security_controls.py

Docker Compose and Playwright browser E2E were not executed in this sandbox. Run them locally with Docker and browser tooling installed.
