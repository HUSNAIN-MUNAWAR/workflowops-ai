# Connectors Validation

Status: **passed**

## Passed

True

## Connectors

- email_demo
- slack_demo
- sheets_demo
- crm_demo
- accounting_demo
- webhook_demo
- file_demo

## Dry Run

- **connector_id**: email_demo
- **action_name**: create_draft
- **status**: dry_run_ok
- **dry_run**: True
- **message**: Dry run passed. No external action executed.
- **data**: {'payload_preview': {'to': 'client@example.com'}}

## Local Write

- **connector_id**: sheets_demo
- **action_name**: append_row
- **status**: row_appended
- **dry_run**: False
- **message**: Local sheet row stored.
- **data**: {'row_id': '3e9854de-7ccc-4235-a857-c288f21466f0'}

## Blocked

- **connector_id**: webhook_demo
- **action_name**: post_json
- **status**: blocked
- **dry_run**: False
- **message**: Webhook URL blocked by localhost-only SSRF guard in demo mode.
- **data**: {'url': 'http://169.254.169.254/latest'}
