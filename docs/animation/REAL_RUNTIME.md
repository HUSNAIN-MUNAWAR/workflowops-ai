# WorkflowOps real runtime evidence

This evidence is produced by executing the repository's actual workflow path,
not by animating invented node states.

## Reproduce

```powershell
$env:PYTHONPATH = "backend"
py -3.12 -u scripts/generate_real_runtime_video.py
```

The runner executes `scripts/generate_workflow_animation.py::build_manifest`,
which calls `MockLLMProvider.complete` and `run_template` for the checked-in
synthetic invoice fixture. It then holds each of the eight data-driven workflow
events for four frames so the trace is readable, writes the actual node outputs
to CSV, and records hashes in the JSON report.

## Model and safety boundary

- provider: `backend/app/llm/mock_provider.py::MockLLMProvider`
- engine: `backend/app/workflows/engine.py::WorkflowEngine`
- learned checkpoint: none
- input: synthetic invoice fixture only
- non-simulation status: `waiting_approval`
- connector preview: `dry_run: true`, `executed: false`

The mock provider is intentionally deterministic rule-based demo logic. No live
LLM, payment, accounting export, or external connector write runs locally. The
video and report must not be used as learned-model or production accuracy proof.

## Artifacts

- `runtime-evidence/workflowops-runtime.mp4` — execution trace.
- `runtime-evidence/workflowops-runtime-poster.png` — first frame.
- `runtime-evidence/workflowops-node-trace.csv` — actual node status, attempts,
  and serialized outputs.
- `runtime-evidence/workflowops-runtime-summary.json` — source hash, provider
  identity, workflow state, engine outputs, runtime versions, and output hashes.
