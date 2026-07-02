# Technical Deep Dive

The backend uses FastAPI, SQLAlchemy, Alembic, Pydantic schemas, RBAC dependencies, audit services, and a persisted DAG scheduler. The frontend uses Next.js App Router, TypeScript, Tailwind, and a small API client layer.

The most important design choice is separating AI recommendations from external actions. Workflow nodes can extract, score, and recommend, but connector actions pass through RBAC and policy checks and are approval-gated where risk requires it.

The reliability tester is intentionally part of the product, not an afterthought. It documents failure modes, evidence, mitigations, and replay IDs.
