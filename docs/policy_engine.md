# Policy Engine

The policy engine evaluates workflow and connector decisions using organization-level defaults and optional workflow-level overrides.

Policy controls include:

- Allowed workflow templates
- Allowed connectors
- Roles allowed to start or approve workflows
- Invoice approval amount threshold
- Risk threshold for review
- External action allowlist
- Max retry count
- Max workflow runtime
- Max estimated cost
- PII handling mode
- Prompt injection action mode
- Document confidence threshold
- Required approval count
- Escalation rules

Every decision returns:

- `allowed`
- `requires_approval`
- `reason`
- `matched_rules`
- `required_roles`
- `risk_level`
- `recommended_action`

Policy decisions are recorded in audit logs and visible in workflow timelines.
