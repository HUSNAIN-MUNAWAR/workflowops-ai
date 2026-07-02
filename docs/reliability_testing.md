# Workflow EvalBench Reliability Testing

`workflow_evalbench` is the signature module of WorkflowOps AI. It tests whether automations behave safely before connecting real tools.

The final suite includes 25 synthetic scenarios covering:

- Document corruption
- Missing fields
- Duplicate invoice
- Vendor/PO mismatch
- Prompt injection and hidden PDF instructions
- Fake approval notes
- Unauthorized connector actions
- Approval bypass attempts
- High-risk escalation
- Low-confidence extraction
- Unsupported documents
- Timeout, retry exhaustion, and loop guard cases
- Wrong branch routing
- Report failure
- Connector failure
- Webhook SSRF attempt
- Cost budget exceeded
- PII leakage attempt
- Role permission violation
- Stale workflow version
- Replay after failed step

The report intentionally avoids a fake perfect score and includes two demo gaps with mitigation recommendations.
