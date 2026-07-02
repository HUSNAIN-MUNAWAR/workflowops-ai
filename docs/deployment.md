# Deployment

## Local SQLite demo

```bash
python -m pip install -r backend/requirements.txt
cd frontend && npm install --no-audit --no-fund && cd ..
make db-upgrade
make seed
PYTHONPATH=backend uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
cd frontend && NEXT_PUBLIC_API_URL=http://localhost:8000 npm run dev
```

## Worker

```bash
make worker
```

The worker supports local sync mode for tests and RQ/Redis-style mode for Docker-style operation.

## Docker

```bash
docker compose config
docker compose up --build
```

Docker could not be executed in the package sandbox because Docker CLI was unavailable. The configuration is included for local verification.

## Production-style example

`docker-compose.prod.example.yml` adds nginx, Postgres, Redis, backend, worker, and frontend. It is an example, not a hardened production deployment.

## Database lifecycle

```bash
make db-upgrade
make db-downgrade
make db-reset
make demo-reset
```

## Backup/restore notes

For PostgreSQL, use `pg_dump` and `pg_restore`. Back up local demo storage separately. Verify restore against a staging environment before production use.
