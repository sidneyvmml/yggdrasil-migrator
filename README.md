# Yggdrasil Migrator

Backend: FastAPI + Celery + Redis + Motor
Frontend: Vue 3 + Pinia + Tailwind

## Feature flags

- Backend (`backend/.env`):
	- `ENABLE_MONGO_TO_KEYCLOAK_MIGRATION=false` keeps Keycloak migrations in Keycloak -> Keycloak only mode.
	- Set to `true` to re-enable MongoDB -> Keycloak migration.
- Frontend (`frontend/.env`):
	- `VITE_ENABLE_MONGO_TO_KEYCLOAK_MIGRATION=false` applies the same restriction in the UI.
	- Set to `true` to show MongoDB -> Keycloak as selectable again.

## Run backend

1. Install dependencies:

```bash
python -m pip install -e .
pip install -r requirements-dev.txt
```

2. Start Redis

3. Start Celery worker:

```bash
cd backend
celery -A app.workers.celery_app.celery worker --loglevel=info
```

4. Start FastAPI:

```bash
cd backend
uvicorn app.main:app --reload
```

## Run frontend

```bash
cd frontend
npm install
npm run dev
```
