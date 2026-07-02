# Security Model

Implemented controls:

- JWT-style authentication with expiry.
- Password hashing through backend security utilities.
- Role-based permissions for admin, automation_manager, reviewer, and viewer.
- Organization scoping for persisted records in demo APIs.
- Upload file type allowlist and size settings.
- Prompt injection detection for uploaded or extracted text.
- PII/secret redaction helpers.
- Webhook connector SSRF guard with localhost-only demo execution.
- Connector allowlist and action policy checks.
- Denied-action audit logs.
- Safe error responses for expected policy/security failures.

Threats documented but requiring production review:

- Real credential storage and rotation.
- Tenant isolation and row-level authorization audit.
- Network egress restrictions.
- Supply-chain hardening.
- Full rate limiting and WAF controls.
- Formal compliance mapping.

No real secrets are committed. `.env.example` uses demo placeholders.
