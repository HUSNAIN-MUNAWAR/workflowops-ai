# API Reference

OpenAPI is available at `/docs` and `/openapi.json` when the backend is running.

Main groups:

- Auth: `/auth/login`, `/auth/me`
- Dashboard: `/dashboard/summary`, `/dashboard/recent-runs`, `/dashboard/risk-distribution`
- Workflow templates: `/workflow-templates`, `/workflow-templates/{template_id}`
- Workflow runs: create, enqueue, resume, replay, cancel, timeline
- Approvals: list, approve, reject, request changes
- Documents: upload, list, extracted fields
- Reports: list, detail, download as JSON/Markdown/HTML/PDF
- Reliability tests: run, list, detail, report
- Policies: default policy, update policy, evaluate policy
- Connectors: list, test, dry-run, execute
- Queue: status, failed jobs, retry
- Audit logs, health, readiness, metrics
