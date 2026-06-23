# AGENTS.md

Purpose: help AI coding agents become productive quickly in this repository.

## Scope
- Monorepo with FastAPI backend, Celery worker, Vue frontend, and pytest tests.
- Prefer minimal, safe changes. Do not touch unrelated files.

## Key Links
- Main setup and dependency install: [README.md](README.md)
- Mongo API request examples: [MONGODB_API_TESTING.md](MONGODB_API_TESTING.md)

## Run Commands
- Full stack from repo root:
  - `npm run dev`
- Backend API from repo root:
  - `python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload`
- Backend API from backend folder:
  - `python -m uvicorn app.main:app --reload`
- Celery worker:
  - `cd backend && celery -A app.workers.celery_app.celery worker --loglevel=info`
- Frontend:
  - `cd frontend && npm run dev`
- Tests:
  - `pytest -q`

## Required Local Services
- Redis must be running for Celery broker/result backend.
- API and worker are separate processes and both must be running to execute migration jobs.

## Architecture Map
- Backend app: `backend/app/main.py`
- Config and env loading: `backend/app/config.py`
- Job/template persistence: `backend/app/db.py` (SQLite)
- Routers:
  - Exploration endpoints: `backend/app/routers/exploration.py`
  - Migration preview/execute: `backend/app/routers/migration.py`
  - Job operations: `backend/app/routers/jobs.py`
  - Templates: `backend/app/routers/templates.py`
- Core migration logic: `backend/app/services/migration_service.py`
- Celery app/task entrypoints: `backend/app/workers/celery_app.py`, `backend/app/workers/tasks.py`
- Frontend main view/state: `frontend/src/App.vue`

## Conventions Agents Should Follow
- Backend is async-first (Motor + FastAPI). Keep new IO paths async.
- Reuse existing path helpers for mapping (`read_value_by_path`, `write_value_by_path`) when adding transforms.
- Keep user-facing errors actionable and concise.
- Preserve existing API schema behavior for backward compatibility when possible.
- Add focused regression tests in `tests/` for migration pipeline changes.

## Known Pitfalls
- Redis auth/env mismatch can break worker startup. Settings are loaded from `backend/.env`.
- If API startup says address already in use, a previous uvicorn instance is already running.
- Mapping paths cannot contain segments starting with `$`.
  - Treat Extended JSON helper objects as leaf values (example: map `_id`, not `_id.$binary.base64`).
- If jobs show pending forever, worker is likely not running.

## Practical Debug Checklist
1. Confirm API reachable on port 8000.
2. Confirm worker connected to Redis and listening to `celery` queue.
3. Check job row/result in SQLite (`yggdrasil.db`) through jobs endpoints.
4. For zero inserts, inspect `processed/inserted/skipped/errors` and verify filter + flatten config.

## Editing Guidelines
- Prefer small patches over broad refactors.
- Do not reformat unrelated code.
- Update or add tests for behavior changes.
- When changing migration payload shape, update both frontend payload builder and backend schema/normalization.
