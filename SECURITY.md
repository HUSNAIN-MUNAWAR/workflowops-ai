# Security Policy

WorkflowOps AI uses synthetic data and local-safe connector behavior for demonstration and validation. Do not put real secrets, customer data, regulated documents, payment credentials, or production connector tokens into this repository.

## Implemented demo controls

- JWT-style auth with expiry.
- Password hashing utilities.
- RBAC for admin, automation_manager, reviewer, and viewer.
- Organization-scoped demo records.
- Upload file type allowlist and file size settings.
- Prompt injection detection for uploaded/extracted text.
- PII/secret redaction helper patterns.
- Connector allowlist and approval-gated high-risk actions.
- Webhook connector SSRF guard with localhost-only demo mode.
- Audit logs for login, upload, workflow start, approvals, connector actions, reports, reliability tests, and access denied events.

## Reporting issues

Use GitHub security advisories or the repository's standard private reporting path for sensitive issues. No dedicated production disclosure mailbox is published with this demo project.

## Production hardening required

Before any production use, complete:

- Secrets vault and credential rotation.
- Tenant isolation and authorization audit.
- Network egress controls.
- Full rate limiting and WAF/reverse proxy rules.
- Logging/monitoring/alerting review.
- Backup/restore testing.
- Connector-specific threat modeling.
- Compliance and legal review for the target domain.
