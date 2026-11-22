# WorkflowOps approval reel storyboard

| Scene | Visual cue | Evidence shown | Gate |
| --- | --- | --- | --- |
| 01 · receive | Invoice run enters the route | Synthetic filename, action type, SHA-256 | Input is explicit and traceable |
| 02 · ingest | Privacy boundary lights up | Redaction and prompt-injection findings | Untrusted text is handled before extraction |
| 03 · extract | Model/reference station activates | Mock provider, confidence, extracted fields | Proposal is not an external action |
| 04 · validate | Missing-field warning appears | `due_date` validation result | Incomplete data remains reviewable |
| 05 · risk | Risk score moves to medium | Score and payment intent | Policy context is visible |
| 06 · approve | Token pauses in amber | `waiting_approval` | Human approval is required |
| 07 · connector | Dry-run preview appears | `accounting_demo`, `dry_run`, `executed` | No external write occurs |
| 08 · audit | Evidence trail closes the loop | Engine events and gated node count | Replay and review remain possible |

Exact values are generated into `workflow_approval_sequence.json`. The reel is a synthetic safety walkthrough, not a live payment or delivery demonstration.
