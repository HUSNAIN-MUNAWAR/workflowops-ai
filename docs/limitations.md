# Limitations

- Synthetic demo data only.
- Deterministic rule-based MockLLMProvider; no claimed LLM benchmark.
- Demo connectors are local and safe; they do not send real messages, payments, CRM updates, or accounting exports.
- OCR/layout extraction is lightweight and demo-validated only.
- RQ/Redis worker support is included, but sandbox validation used local sync mode.
- Alembic migration is an initial metadata migration, not a long production migration history.
- Playwright E2E is scaffolded; browser run requires local tooling.
- Not certified accounting, legal, SOC 2, ISO 27001, or compliance software.
- Production use needs security review, tenant isolation review, monitoring, backups, secrets management, and domain validation.
