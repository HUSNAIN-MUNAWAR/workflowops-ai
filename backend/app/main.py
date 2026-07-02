from __future__ import annotations
from contextlib import asynccontextmanager
from uuid import uuid4
from fastapi import FastAPI, Request, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import get_settings
from app.core.logging import configure_logging
from app.db.session import SessionLocal, has_tables, init_db
from app.db.seed import seed_database
from app.api.routes import approvals, audit_logs, auth, connectors, dashboard, demo, documents, health, policies, queue, reliability, reports, workflow_builder, workflow_runs, workflow_templates
settings=get_settings(); configure_logging()

@asynccontextmanager
async def lifespan(_app: FastAPI):
    if settings.auto_create_tables or (settings.environment in {"test","local"} and not has_tables()):
        init_db(drop_existing=False); db=SessionLocal();
        try: seed_database(db,reset=False)
        finally: db.close()
    yield

app=FastAPI(title=settings.app_name,version="3.0.0",description="Governed AI workflow automation platform - portfolio-grade synthetic demo with persisted DAG workflows, policies, connectors and audit logs.", lifespan=lifespan)
origins=[x.strip() for x in settings.allowed_origins.split(',') if x.strip()]+(["*"] if settings.environment=="local" else [])
app.add_middleware(CORSMiddleware,allow_origins=origins,allow_credentials=True,allow_methods=["*"],allow_headers=["*"])
@app.middleware("http")
async def request_id_and_security_headers(request:Request,call_next):
    request.state.request_id=request.headers.get("x-request-id") or str(uuid4()); response=await call_next(request); response.headers["x-request-id"]=request.state.request_id; response.headers["x-content-type-options"]="nosniff"; response.headers["x-frame-options"]="DENY"; response.headers["referrer-policy"]="no-referrer"; return response
for r in [health.router,auth.router,dashboard.router,workflow_templates.router,workflow_builder.router,workflow_runs.router,approvals.router,documents.router,reports.router,reliability.router,audit_logs.router,connectors.router,policies.router,queue.router,demo.router]: app.include_router(r)
@app.websocket("/ws/runs/{run_id}")
async def workflow_updates(websocket:WebSocket,run_id:str):
    await websocket.accept(); await websocket.send_json({"run_id":run_id,"event":"connected","message":"WebSocket demo channel ready. Poll /workflow-runs/{run_id}/timeline for persisted DAG events."}); await websocket.close()
