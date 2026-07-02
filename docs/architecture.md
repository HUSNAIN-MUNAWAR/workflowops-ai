# Architecture

WorkflowOps AI uses a layered architecture:

- Next.js frontend for dashboard, workflow builder, approvals, connectors, policies, reports, and audit logs.
- FastAPI backend exposing typed REST APIs and OpenAPI docs.
- SQLAlchemy persistence with SQLite for local demo and PostgreSQL for Docker.
- Persisted DAG scheduler for workflow node execution and replay.
- Queue abstraction supporting local sync mode and RQ/Redis-style background execution.
- Safe connector registry with local demo connector implementations.
- Tenant policy engine for approval thresholds, connector allowlists, risk decisions, and document confidence rules.
- Document intelligence layer for PDF extraction, optional OCR fallback, classification, field extraction, warnings, and prompt-injection detection.
- Report generator for JSON, Markdown, HTML, and PDF outputs.

This is production-style architecture but not production-certified software.
