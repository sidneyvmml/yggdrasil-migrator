# Yggdrasil Migrator

Backend: FastAPI + Celery + Redis + Motor
Frontend: Vue 3 + Pinia + Tailwind

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
