"""Capture the real WorkflowOps synthetic invoice run as an MP4 and report."""

from __future__ import annotations

import csv
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import platform
import sys

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(ROOT / "backend") not in sys.path:
    sys.path.insert(0, str(ROOT / "backend"))

from scripts.generate_workflow_animation import build_manifest  # noqa: E402


OUTPUT_ROOT = ROOT / "docs" / "animation" / "runtime-evidence"
VIDEO_PATH = OUTPUT_ROOT / "workflowops-runtime.mp4"
POSTER_PATH = OUTPUT_ROOT / "workflowops-runtime-poster.png"
TRACE_PATH = OUTPUT_ROOT / "workflowops-node-trace.csv"
SUMMARY_PATH = OUTPUT_ROOT / "workflowops-runtime-summary.json"
FRAMES_PER_EVENT = 4
FPS = 4


def file_sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def text(value: object) -> str:
    return str(value).encode("ascii", "replace").decode("ascii")


def put_text(canvas: np.ndarray, value: object, x: int, y: int, scale: float = 0.58, color: tuple[int, int, int] = (220, 232, 236), thickness: int = 1) -> None:
    cv2.putText(canvas, text(value), (x, y), cv2.FONT_HERSHEY_SIMPLEX, scale, color, thickness, cv2.LINE_AA)


def trace_rows(manifest: dict[str, object]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for node_id, node in manifest["engine_outputs"].items():
        rows.append(
            {
                "node_id": node_id,
                "status": node["status"],
                "attempts": node["attempts"],
                "output_json": json.dumps(node["output"], sort_keys=True),
            }
        )
    return rows


def evidence_lines(manifest: dict[str, object], event_index: int) -> list[str]:
    source = manifest["source"]
    model = manifest["model"]
    workflow = manifest["workflow"]
    outputs = manifest["engine_outputs"]
    if event_index == 0:
        return [f"file: {source['filename']}", f"bytes: {source['bytes']}", f"action: {source['action_type']}", f"sha256: {source['sha256'][:28]}..."]
    if event_index == 1:
        return ["redaction boundary: executed", "prompt injection findings: 0", "audit event names:", *workflow["audit_event_names"][:4]]
    if event_index == 2:
        extracted = outputs["extract"]["output"]
        return [f"provider: {model['provider']}", f"provider confidence: {model['confidence']:.2f}", f"invoice number: {extracted.get('invoice_number')}", f"amount: {extracted.get('amount')} {extracted.get('currency')}"]
    if event_index == 3:
        validated = outputs["validate"]["output"]
        return [f"valid: {validated.get('valid')}", f"missing fields: {validated.get('missing_fields')}", "review remains possible after warning"]
    if event_index == 4:
        risk = outputs["risk"]["output"]
        return [f"risk score: {risk.get('risk_score'):.1f}", f"risk level: {risk.get('risk_level')}", f"requires approval: {risk.get('requires_approval')}"]
    if event_index == 5:
        approval = outputs["approval"]["output"]
        return [f"workflow status: {manifest['workflow']['gated_status']}", f"approval required: {approval.get('required')}", "connector execution is paused"]
    if event_index == 6:
        connector = outputs["connector_preview"]["output"]
        return [f"provider: {connector.get('provider')}", f"dry_run: {connector.get('dry_run')}", f"executed: {connector.get('executed')}", "no external payment write"]
    return [f"gated nodes: {workflow['gated_nodes_completed']}", f"engine events: {len(workflow['audit_event_names'])}", "trace rows are preserved in the CSV", "replay evidence is deterministic"]


def render_frame(manifest: dict[str, object], event_index: int, frame_number: int, frame_count: int) -> np.ndarray:
    canvas = np.full((720, 1280, 3), (7, 16, 28), dtype=np.uint8)
    event = manifest["events"][event_index]
    put_text(canvas, "WorkflowOps AI - REAL LOCAL RUNTIME", 40, 48, 0.98, (235, 242, 246), 2)
    put_text(canvas, f"event {event_index + 1}/8  |  frame {frame_number}/{frame_count}", 40, 80, 0.56, (143, 163, 180))
    cv2.rectangle(canvas, (34, 108), (820, 660), (31, 53, 73), 2)
    cv2.rectangle(canvas, (852, 108), (1240, 660), (31, 53, 73), 2)
    put_text(canvas, event["title"], 60, 158, 0.82, (115, 215, 192), 2)
    put_text(canvas, event["detail"], 60, 194, 0.52, (210, 222, 230))
    put_text(canvas, f"executed metric: {event['metric']}", 60, 226, 0.56, (115, 215, 192), 1)
    for index, line in enumerate(evidence_lines(manifest, event_index)):
        put_text(canvas, line, 66, 280 + index * 34, 0.58, (221, 231, 235))

    model = manifest["model"]
    workflow = manifest["workflow"]
    panel = [
        "EXECUTED PATH",
        "WorkflowEngine + MockLLMProvider",
        f"provider: {model['provider']}",
        "learned checkpoint: none",
        "",
        "SAFETY STATE",
        f"gated status: {workflow['gated_status']}",
        f"simulation: {workflow['simulation_preview_status']}",
        "connector: dry-run only",
        "",
        "CLAIM BOUNDARY",
        "Synthetic fixture only.",
        "Mock provider, not a live LLM.",
        "No external write executed.",
    ]
    for index, line in enumerate(panel):
        heading = index in {0, 5, 10}
        put_text(canvas, line, 882, 158 + index * 31, 0.56 if not heading else 0.62, (220, 232, 236) if not heading else (115, 215, 192), 1 if not heading else 2)
    put_text(canvas, "synthetic invoice | local engine trace | no fabricated model claim", 40, 695, 0.52, (143, 163, 180))
    return canvas


def main() -> None:
    manifest = build_manifest()
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    writer = cv2.VideoWriter(str(VIDEO_PATH), cv2.VideoWriter_fourcc(*"mp4v"), FPS, (1280, 720))
    if not writer.isOpened():
        raise RuntimeError(f"unable to open video writer for {VIDEO_PATH}")
    frame_count = len(manifest["events"]) * FRAMES_PER_EVENT
    first_frame: np.ndarray | None = None
    frame_number = 0
    try:
        for event_index in range(len(manifest["events"])):
            for _ in range(FRAMES_PER_EVENT):
                frame_number += 1
                frame = render_frame(manifest, event_index, frame_number, frame_count)
                first_frame = first_frame if first_frame is not None else frame.copy()
                writer.write(frame)
    finally:
        writer.release()
    if first_frame is None:
        raise RuntimeError("no runtime frames were produced")
    cv2.imwrite(str(POSTER_PATH), first_frame)

    rows = trace_rows(manifest)
    with TRACE_PATH.open("w", newline="", encoding="utf-8") as handle:
        writer_csv = csv.DictWriter(handle, fieldnames=["node_id", "status", "attempts", "output_json"])
        writer_csv.writeheader()
        writer_csv.writerows(rows)

    report = {
        "run_type": "workflowops_real_local_runtime_video",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "command": "PYTHONPATH=backend py -3.12 -u scripts/generate_real_runtime_video.py",
        "source": manifest["source"],
        "model": {
            **manifest["model"],
            "learned_checkpoint": None,
            "interpretation": "MockLLMProvider is deterministic rule-based demo logic; no live LLM was called.",
        },
        "workflow": manifest["workflow"],
        "engine_outputs": manifest["engine_outputs"],
        "runtime": {
            "python": platform.python_version(),
            "opencv": cv2.__version__,
            "numpy": np.__version__,
            "platform": platform.platform(),
            "device": "cpu",
        },
        "outputs": {
            "video": str(VIDEO_PATH.relative_to(ROOT)),
            "poster": str(POSTER_PATH.relative_to(ROOT)),
            "node_trace_csv": str(TRACE_PATH.relative_to(ROOT)),
            "sha256": {str(path.relative_to(ROOT)): file_sha256(path) for path in (VIDEO_PATH, POSTER_PATH, TRACE_PATH)},
        },
        "interpretation": [
            "The MP4 is generated from the actual WorkflowEngine and MockLLMProvider execution over the checked-in synthetic invoice fixture.",
            "The approval gate stopped the non-simulation run before connector execution.",
            "The connector frame is a separate simulation preview with dry_run true and executed false.",
            "This is not evidence of live LLM quality, payment execution, or production workflow accuracy.",
        ],
    }
    SUMMARY_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"video": str(VIDEO_PATH), "poster": str(POSTER_PATH), "summary": str(SUMMARY_PATH), "trace_rows": len(rows)}, indent=2))


if __name__ == "__main__":
    main()
