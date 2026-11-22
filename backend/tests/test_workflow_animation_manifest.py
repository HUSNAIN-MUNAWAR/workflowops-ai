from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "docs" / "animation" / "workflow_approval_sequence.json"
REEL = ROOT / "frontend" / "public" / "animation" / "workflow-approval-reel.html"


def test_workflow_animation_uses_gated_real_run() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/generate_workflow_animation.py"],
        cwd=ROOT,
        env={**os.environ, "PYTHONPATH": "backend"},
        check=True,
        capture_output=True,
        text=True,
    )
    assert "gated status: waiting_approval" in result.stdout

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    reel = REEL.read_text(encoding="utf-8")
    assert manifest["model"]["provider"] == "mock"
    assert manifest["model"]["deterministic"] is True
    assert manifest["workflow"]["gated_status"] == "waiting_approval"
    assert manifest["engine_outputs"]["connector_preview"]["output"]["dry_run"] is True
    assert manifest["engine_outputs"]["connector_preview"]["output"]["executed"] is False
    assert len(manifest["events"]) == 8
    assert "waiting_approval" in reel
    assert "synthetic fixture" in reel.lower()
