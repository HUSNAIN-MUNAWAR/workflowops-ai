# Persisted DAG Scheduler

The DAG scheduler persists workflow runs and step runs before and after node execution. Each node stores input/output snapshots, status, retry count, duration, and error message.

Supported states include pending, queued, running, waiting_for_approval, waiting_for_dependency, succeeded, failed, skipped, cancelled, and timed_out.

Supported node types include ingest_document, classify_document, extract_fields, validate_fields, score_risk, create_task, request_approval, generate_draft, export_report, connector_action, notify_user, wait_for_human, branch, merge, and stop.

Demo behavior:

- Invoice workflows pause at approval gates when risk/amount policy requires human review.
- Approval resumes execution and completes remaining nodes.
- Rejected approval routes the run to a failed/rejected branch in demo mode.
- Replay can reset and re-run a failed/completed node from persisted snapshots.
- Cancellation prevents further queued steps.

Production hardening required: distributed locking, idempotency enforcement across real connectors, worker concurrency tests, and state transition race-condition testing.
