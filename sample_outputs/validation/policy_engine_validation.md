# Policy Engine Validation

Status: **passed**

## Passed

True

## Approval Decision

- **allowed**: True
- **requires_approval**: True
- **reason**: Invoice amount 5000.0 exceeds approval threshold 1000.0.
- **matched_rules**: ['invoice_approval_threshold']
- **required_roles**: ['admin', 'reviewer']
- **risk_level**: medium
- **recommended_action**: request_approval

## Block Decision

- **allowed**: False
- **requires_approval**: True
- **reason**: Prompt injection indicator detected; action blocked/quarantined by policy.
- **matched_rules**: ['risk_review_threshold', 'prompt_injection_action_mode']
- **required_roles**: ['admin', 'reviewer']
- **risk_level**: high
- **recommended_action**: block
