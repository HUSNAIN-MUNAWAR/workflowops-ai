# WorkflowOps approval animation enhancement

## Purpose

Show the safety-critical path that makes WorkflowOps credible: a synthetic payment request is redacted, extracted, validated, risk-scored, paused for human approval, and only previewed at the connector boundary.

## Real repository boundaries

The generated reel executes the repository’s actual code:

- `backend/app/workflows/engine.py::WorkflowEngine` runs the `invoice_approval` template.
- `backend/app/core/security.py` performs redaction and prompt-injection detection.
- `backend/app/documents/classifier.py` and `backend/app/documents/extraction.py` classify and extract fields.
- `backend/app/llm/mock_provider.py::MockLLMProvider` supplies the deterministic model-reference output.
- `backend/app/workflows/approvals.py` produces the approval request.
- The simulation preview reaches `accounting_demo` with `dry_run: true` and `executed: false`.

The provider is intentionally labeled as a deterministic demo provider, not as a learned-model accuracy benchmark. The fixture is synthetic and no payment, email, or external connector action is sent.

## Reproduce

```bash
PYTHONPATH=backend python scripts/generate_workflow_animation.py
```

Outputs:

- `docs/animation/workflow_approval_sequence.json` — source checksum, model reference, stable workflow outputs, and scene events.
- `frontend/public/animation/workflow-approval-reel.html` — self-contained animated reel with pause, replay, and stage selection.
