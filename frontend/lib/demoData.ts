export const metrics = [
  { label: 'Workflow runs', value: '248' },
  { label: 'Pending approvals', value: '17' },
  { label: 'Failed automations', value: '6' },
  { label: 'Avg reliability', value: '94%' },
  { label: 'Documents processed', value: '1,284' },
  { label: 'SLA breaches', value: '3' }
]

export const templates = [
  { name: 'Invoice Approval', path: '/templates/invoice', risk: 'Medium', description: 'PO matching, duplicate detection, approval chain, payment-ready export.' },
  { name: 'Email-to-Task', path: '/templates/email', risk: 'Low', description: 'Inbox classification, SLA timers, draft replies, task routing.' },
  { name: 'RFP Proposal Automation', path: '/templates/rfp', risk: 'High', description: 'Requirements extraction, compliance matrix, bid/no-bid scoring.' },
  { name: 'Compliance Evidence', path: '/templates/compliance', risk: 'High', description: 'Map evidence to controls, missing evidence tasks, audit report.' },
  { name: 'Support Escalation', path: '/templates/support', risk: 'Medium', description: 'Anger/refund/legal/VIP detection, response draft, escalation queue.' },
  { name: 'Reliability Tester', path: '/templates/reliability', risk: 'High', description: 'Scenario-based safety testing, replay logs, mitigation report.' }
]

export const latestRuns = [
  { id: 'RUN-1024', template: 'Invoice Approval', status: 'Waiting approval', risk: 82 },
  { id: 'RUN-1023', template: 'Email-to-Task', status: 'Completed', risk: 22 },
  { id: 'RUN-1022', template: 'RFP Proposal', status: 'Exception', risk: 76 },
  { id: 'RUN-1021', template: 'Support Escalation', status: 'Escalated', risk: 88 }
]
