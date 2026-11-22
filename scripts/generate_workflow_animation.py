"""Generate an executable, model-referenced WorkflowOps approval animation."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from textwrap import dedent

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.llm.mock_provider import MockLLMProvider  # noqa: E402
from app.workflows.runner import run_template  # noqa: E402


SOURCE = ROOT / "demo_data" / "animation" / "synthetic_invoice_approval.json"
MANIFEST = ROOT / "docs" / "animation" / "workflow_approval_sequence.json"
REEL = ROOT / "frontend" / "public" / "animation" / "workflow-approval-reel.html"


def stable_node_result(result: object) -> dict[str, object]:
    output = dict(result.output)
    if "approval" in output:
        output["approval"] = {
            key: value
            for key, value in output["approval"].items()
            if key not in {"approval_id", "created_at"}
        }
    return {
        "node_id": result.node_id,
        "status": result.status.value,
        "output": output,
        "attempts": result.attempts,
    }


def build_manifest() -> dict[str, object]:
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    raw_text = source["text"]
    source_bytes = SOURCE.read_bytes()
    provider = MockLLMProvider()
    provider_response = provider.complete("invoice extraction", raw_text)

    gated = run_template(
        "invoice_approval",
        {"text": raw_text, "filename": source["filename"], "action_type": source["action_type"]},
        simulation_mode=False,
    )
    preview = run_template(
        "invoice_approval",
        {"text": raw_text, "filename": source["filename"], "action_type": source["action_type"]},
        simulation_mode=True,
    )
    gated_results = [stable_node_result(result) for result in gated.node_results]
    preview_results = [stable_node_result(result) for result in preview.node_results]
    extract = next(result for result in gated_results if result["node_id"] == "extract")
    validate = next(result for result in gated_results if result["node_id"] == "validate")
    risk = next(result for result in gated_results if result["node_id"] == "risk")
    approval = next(result for result in gated_results if result["node_id"] == "approval")
    connector = next(result for result in preview_results if result["node_id"] == "export")

    return {
        "schema_version": "1.0",
        "fixture": source["fixture_id"],
        "source": {
            "path": SOURCE.relative_to(ROOT).as_posix(),
            "filename": source["filename"],
            "bytes": len(source_bytes),
            "sha256": hashlib.sha256(source_bytes).hexdigest(),
            "synthetic": True,
            "action_type": source["action_type"],
        },
        "model": {
            "name": "workflowops-mock-provider",
            "implementation": "backend/app/llm/mock_provider.py::MockLLMProvider",
            "provider": provider_response.provider,
            "deterministic": provider_response.deterministic,
            "confidence": provider_response.confidence,
            "claim_boundary": "Deterministic rule-based demo provider; not a production accuracy benchmark.",
            "reference_output": provider_response.data,
        },
        "workflow": {
            "template": "invoice_approval",
            "engine": "backend/app/workflows/engine.py::WorkflowEngine",
            "gated_status": gated.status,
            "simulation_preview_status": preview.status,
            "gated_nodes_completed": len(gated.node_results),
            "simulation_nodes_completed": len(preview.node_results),
            "audit_event_names": [event["event"] for event in gated.events],
        },
        "engine_outputs": {
            "extract": extract,
            "validate": validate,
            "risk": risk,
            "approval": approval,
            "connector_preview": connector,
        },
        "events": [
            {
                "id": "receive",
                "short": "Receive",
                "title": "Synthetic invoice received",
                "detail": "The fixture enters the invoice approval workflow with an explicit payment-export intent.",
                "metric": f"{source['filename']} · {len(source_bytes):,} bytes",
                "status": "input",
            },
            {
                "id": "ingest",
                "short": "Ingest",
                "title": "Ingest and redact",
                "detail": "The engine redacts sensitive-looking values and records prompt-injection findings before extraction.",
                "metric": "redaction boundary · 0 injection findings",
                "status": "guarded",
            },
            {
                "id": "extract",
                "short": "Extract",
                "title": "Model reference + extraction",
                "detail": "The deterministic mock provider and repository extraction rules produce an invoice field proposal.",
                "metric": f"{provider_response.provider} · {provider_response.confidence:.0%} provider confidence",
                "status": "proposed",
            },
            {
                "id": "validate",
                "short": "Validate",
                "title": "Required fields checked",
                "detail": "Validation catches the date-shaped value removed by the privacy boundary and keeps the workflow reviewable.",
                "metric": "blocked field · due_date missing",
                "status": "warning",
            },
            {
                "id": "risk",
                "short": "Risk",
                "title": "Risk score computed",
                "detail": "Payment intent plus the validation warning raise the run into the approval path.",
                "metric": f"risk {risk['output']['risk_score']:.1f} · {risk['output']['risk_level']}",
                "status": "scored",
            },
            {
                "id": "approval",
                "short": "Approve",
                "title": "Human approval required",
                "detail": "The non-simulation engine pauses before any connector action can execute.",
                "metric": "status waiting_approval",
                "status": "paused",
            },
            {
                "id": "connector",
                "short": "Connector",
                "title": "Safe connector preview",
                "detail": "A separate simulation run shows the accounting action boundary without performing an external write.",
                "metric": "accounting_demo · dry_run true · executed false",
                "status": "dry-run",
            },
            {
                "id": "audit",
                "short": "Audit",
                "title": "Replayable evidence recorded",
                "detail": "The workflow events, node outputs, approval state, and model boundary remain available for review.",
                "metric": f"{len(gated.events)} engine events · {len(gated.node_results)} gated nodes",
                "status": "traceable",
            },
        ],
    }


def reel_html(manifest: dict[str, object]) -> str:
    sequence = json.dumps(manifest, indent=2, sort_keys=True).replace("</", "<\\/")
    return dedent(
        f"""\
        <!doctype html>
        <html lang="en">
        <head>
          <meta charset="utf-8">
          <meta name="viewport" content="width=device-width, initial-scale=1">
          <title>WorkflowOps AI — Approval gate reference reel</title>
          <style>
            :root {{ color-scheme: dark; --ink: #edf3f8; --muted: #9aabba; --line: #283d52; --accent: #73d7c0; --warning: #f3c36f; }}
            * {{ box-sizing: border-box; }}
            body {{ margin: 0; min-width: 320px; background: radial-gradient(circle at 75% 0%, #223a54 0, #0a1320 53%, #060b12 100%); color: var(--ink); font: 15px/1.5 Inter, ui-sans-serif, system-ui, sans-serif; }}
            .reel {{ max-width: 1180px; margin: 0 auto; padding: 42px 28px 34px; }}
            .eyebrow {{ color: var(--accent); font-size: 12px; font-weight: 700; letter-spacing: .14em; text-transform: uppercase; }}
            h1 {{ max-width: 800px; margin: 8px 0 10px; font-size: clamp(28px, 5vw, 52px); line-height: 1.02; letter-spacing: -.04em; }}
            .lede {{ max-width: 760px; margin: 0; color: var(--muted); font-size: 17px; }}
            .model-line {{ display: flex; flex-wrap: wrap; gap: 8px 18px; margin-top: 22px; color: var(--muted); font-size: 12px; }}
            .model-line span::before {{ content: "•"; color: var(--accent); margin-right: 8px; }}
            .stage {{ margin-top: 36px; overflow: hidden; border: 1px solid var(--line); border-radius: 22px; background: linear-gradient(145deg, rgba(20,40,61,.94), rgba(8,17,29,.97)); box-shadow: 0 22px 60px rgba(0,0,0,.28); }}
            svg {{ display: block; width: 100%; height: auto; min-height: 300px; }}
            .route {{ fill: none; stroke: #2a425b; stroke-width: 4; stroke-linecap: round; stroke-dasharray: 7 12; }}
            .station circle {{ fill: #0a1623; stroke: #3b536b; stroke-width: 3; transition: fill .25s ease, stroke .25s ease, transform .25s ease; transform-origin: center; }}
            .station text {{ fill: #8ea1b5; font-size: 14px; text-anchor: middle; }}
            .station .index {{ fill: #c4d1df; font-size: 13px; font-weight: 700; }}
            .station.active circle {{ fill: #164e4a; stroke: var(--accent); transform: scale(1.1); }}
            .station.active text {{ fill: var(--ink); }}
            .station.done circle {{ fill: #162f43; stroke: #5783a7; }}
            .token {{ fill: var(--accent); stroke: #c6fff1; stroke-width: 3; filter: drop-shadow(0 0 12px rgba(115,215,192,.6)); }}
            .token-label {{ fill: #041b19; font-size: 11px; font-weight: 800; text-anchor: middle; }}
            .panel {{ display: grid; grid-template-columns: minmax(0, 1fr) auto; align-items: end; gap: 18px; padding: 22px 24px 24px; border-top: 1px solid var(--line); }}
            .panel h2 {{ margin: 0 0 3px; font-size: 24px; letter-spacing: -.02em; }}
            .panel p {{ margin: 0; color: var(--muted); }}
            .metric {{ color: var(--accent); font-size: 13px; font-weight: 700; text-align: right; }}
            .controls {{ display: flex; gap: 8px; margin-top: 16px; }}
            button {{ border: 1px solid #36506b; border-radius: 999px; padding: 9px 15px; background: #102237; color: var(--ink); font: inherit; cursor: pointer; }}
            button:hover, button:focus-visible {{ border-color: var(--accent); outline: 2px solid rgba(115,215,192,.35); outline-offset: 2px; }}
            .timeline {{ display: grid; grid-template-columns: repeat(4, minmax(120px, 1fr)); gap: 7px; margin-top: 18px; }}
            .timeline button {{ min-height: 60px; border-radius: 12px; padding: 8px; color: var(--muted); text-align: left; font-size: 12px; }}
            .timeline button[aria-current="step"] {{ border-color: var(--accent); background: #153846; color: var(--ink); }}
            .timeline strong {{ display: block; color: inherit; font-size: 11px; text-transform: uppercase; letter-spacing: .08em; }}
            .disclaimer {{ margin-top: 20px; color: var(--muted); font-size: 12px; }}
            @media (max-width: 760px) {{ .reel {{ padding: 28px 16px; }} .panel {{ grid-template-columns: 1fr; }} .metric {{ text-align: left; }} .timeline {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }} svg {{ min-height: 420px; }} }}
            @media (prefers-reduced-motion: reduce) {{ *, *::before, *::after {{ scroll-behavior: auto !important; transition-duration: .01ms !important; animation-duration: .01ms !important; animation-iteration-count: 1 !important; }} }}
          </style>
        </head>
        <body>
          <main class="reel" aria-labelledby="title">
            <div class="eyebrow">WorkflowOps AI · production reference reel</div>
            <h1 id="title">A payment request pauses before it can act</h1>
            <p class="lede">A real synthetic invoice run through the repository’s model boundary, redaction layer, risk policy, approval gate, and safe connector preview.</p>
            <div class="model-line" aria-label="Model and data boundary"><span id="model-name"></span><span id="source-name"></span><span>synthetic data only</span></div>
            <section class="stage" aria-label="Animated workflow approval sequence">
              <svg viewBox="0 0 1210 390" role="img" aria-labelledby="diagram-title diagram-description">
                <title id="diagram-title">Animated WorkflowOps approval stages</title>
                <desc id="diagram-description">A token travels through invoice receipt, redaction, extraction, validation, risk scoring, human approval, dry-run connector preview, and audit evidence.</desc>
                <path class="route" d="M 80 190 C 220 82, 360 82, 510 190 S 800 298, 1130 100" />
                <g id="stations"></g>
                <g aria-hidden="true"><circle id="token" class="token" cx="80" cy="190" r="22"></circle><text id="token-label" class="token-label" x="80" y="194">RUN</text></g>
              </svg>
              <div class="panel" aria-live="polite"><div><h2 id="event-title"></h2><p id="event-detail"></p></div><div id="event-metric" class="metric"></div></div>
            </section>
            <div class="controls"><button id="toggle" type="button">Pause</button><button id="replay" type="button">Replay</button></div>
            <div id="timeline" class="timeline" role="list" aria-label="Animation stages"></div>
            <p class="disclaimer">Synthetic fixture · deterministic demo provider and workflow rules · no payment, email, or external connector action is executed.</p>
          </main>
          <script>
            const sequence = {sequence};
            const events = sequence.events;
            const points = [[80,190],[230,96],[380,96],[530,190],[680,284],[830,284],[980,190],[1130,96]];
            const stations = document.getElementById('stations');
            const timeline = document.getElementById('timeline');
            const token = document.getElementById('token');
            const tokenLabel = document.getElementById('token-label');
            const title = document.getElementById('event-title');
            const detail = document.getElementById('event-detail');
            const metric = document.getElementById('event-metric');
            const toggle = document.getElementById('toggle');
            let current = 0;
            let started = performance.now();
            let playing = !window.matchMedia('(prefers-reduced-motion: reduce)').matches;
            const duration = 1850;
            points.forEach((point, index) => {{
              const group = document.createElementNS('http://www.w3.org/2000/svg', 'g');
              group.classList.add('station');
              group.innerHTML = `<circle cx="${{point[0]}}" cy="${{point[1]}}" r="30"></circle><text class="index" x="${{point[0]}}" y="${{point[1] + 5}}">${{index + 1}}</text><text x="${{point[0]}}" y="${{point[1] + 57}}">${{events[index].short}}</text>`;
              stations.appendChild(group);
            }});
            events.forEach((event, index) => {{
              const item = document.createElement('button');
              item.type = 'button'; item.setAttribute('role', 'listitem'); item.dataset.index = index;
              item.innerHTML = `<strong>${{String(index + 1).padStart(2, '0')}} · ${{event.status}}</strong>${{event.title}}`;
              item.addEventListener('click', () => {{ current = index; started = performance.now(); playing = false; toggle.textContent = 'Play'; render(0); }});
              timeline.appendChild(item);
            }});
            document.getElementById('model-name').textContent = `model ${{sequence.model.name}} · ${{sequence.model.provider}}`;
            document.getElementById('source-name').textContent = `source ${{sequence.source.filename}}`;
            function render(progress) {{
              const next = (current + 1) % points.length;
              const from = points[current], to = points[next];
              const x = from[0] + (to[0] - from[0]) * progress, y = from[1] + (to[1] - from[1]) * progress;
              token.setAttribute('cx', x); token.setAttribute('cy', y); tokenLabel.setAttribute('x', x); tokenLabel.setAttribute('y', y + 4);
              title.textContent = events[current].title; detail.textContent = events[current].detail; metric.textContent = events[current].metric;
              document.querySelectorAll('.station').forEach((node, index) => {{ node.classList.toggle('active', index === current); node.classList.toggle('done', index < current); }});
              timeline.querySelectorAll('button').forEach((node, index) => node.setAttribute('aria-current', index === current ? 'step' : 'false'));
            }}
            function animate(now) {{
              if (playing) {{ const progress = Math.min(1, (now - started) / duration); render(progress); if (progress >= 1) {{ current = (current + 1) % events.length; started = now; }} }} else {{ render(0); }}
              requestAnimationFrame(animate);
            }}
            toggle.addEventListener('click', () => {{ playing = !playing; started = performance.now(); toggle.textContent = playing ? 'Pause' : 'Play'; }});
            document.getElementById('replay').addEventListener('click', () => {{ current = 0; started = performance.now(); playing = true; toggle.textContent = 'Pause'; }});
            render(0); requestAnimationFrame(animate);
          </script>
        </body>
        </html>
        """
    )


def main() -> None:
    manifest = build_manifest()
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    REEL.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REEL.write_text(reel_html(manifest), encoding="utf-8")
    print(f"wrote {MANIFEST.relative_to(ROOT)}")
    print(f"wrote {REEL.relative_to(ROOT)}")
    print(f"source checksum: {manifest['source']['sha256']}")
    print(f"gated status: {manifest['workflow']['gated_status']}")
    print(f"risk score: {manifest['engine_outputs']['risk']['output']['risk_score']}")


if __name__ == "__main__":
    main()
