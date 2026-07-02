from __future__ import annotations
try:
    from fastapi import APIRouter
except Exception:  # pragma: no cover
    APIRouter = None

from app.db.seed import build_demo_seed
from app.workflows.templates import load_builtin_templates
from app.modules.reliability.evalbench import run_reliability_suite

if APIRouter:
    router = APIRouter(prefix="/demo", tags=["demo"])

    @router.get("/seed")
    def seed_preview():
        data = build_demo_seed()
        return {
            "organization": data["organization"].__dict__,
            "users": [{"email": u.email, "role": u.role, "full_name": u.full_name} for u in data["users"]],
            "templates": [t.__dict__ for t in data["templates"]],
        }

    @router.get("/templates")
    def templates():
        return [t.__dict__ for t in load_builtin_templates()]

    @router.get("/reliability")
    def reliability():
        return run_reliability_suite()
else:
    router = None
