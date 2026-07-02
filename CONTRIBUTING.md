# Contributing

Thanks for improving WorkflowOps AI.

## Local Development

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r backend/requirements.txt
PYTHONPATH=backend pytest -q backend/tests
make validate
```

Frontend:

```bash
cd frontend
npm install
npm run typecheck
npm run build
```

## Contribution Standards

- Keep demo data synthetic.
- Do not claim production clients, certifications, revenue, or benchmarks.
- Add tests for workflow engine, approvals, RBAC, provider behavior, and report generation.
- Add validation scripts when new workflow templates are introduced.
- Document limitations honestly.

## Pull Request Checklist

- [ ] Tests pass
- [ ] Validation scripts pass
- [ ] Documentation updated
- [ ] Synthetic examples only
- [ ] No secrets committed
