# Connector Framework

WorkflowOps AI includes a safe demo connector architecture. Real external side effects are disabled by default.

Connectors included:

- Email demo connector: writes draft emails to the database.
- Slack-style demo connector: writes local notification records.
- Google Sheets-style connector: writes local CSV/table rows.
- CRM-style connector: writes local lead/task records.
- Accounting-style connector: writes local invoice export records.
- Webhook connector: dry-run and localhost-only demo mode, with SSRF guard.
- File storage connector: writes local demo files.

Every action supports permission policy, dry-run, approval-required metadata, idempotency key, audit logging, simulated result, and failure simulation.

Production hardening required: OAuth, secrets vaulting, outbound allowlists, idempotency ledgers, customer-owned credentials, network egress control, and connector-specific security review.
