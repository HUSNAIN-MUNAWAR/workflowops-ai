from __future__ import annotations

from app.core.audit import AuditLogger
from app.workflows.engine import WorkflowEngine, WorkflowRun
from app.workflows.templates import WorkflowTemplate, load_builtin_templates


def get_template(slug: str) -> WorkflowTemplate:
    for template in load_builtin_templates():
        if template.slug == slug:
            return template
    raise KeyError(f"Template not found: {slug}")


def run_template(slug: str, payload: dict, simulation_mode: bool = False) -> WorkflowRun:
    engine = WorkflowEngine(AuditLogger(), simulation_mode=simulation_mode)
    return engine.run(get_template(slug), payload)
