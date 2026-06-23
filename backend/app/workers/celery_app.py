from celery import Celery

from app.config import settings
from app.db import SqliteRepository

redis_url = settings.computed_redis_url

celery = Celery(
    "yggdrasil_worker",
    broker=redis_url,
    backend=redis_url,
)

# Worker processes run outside FastAPI startup hooks, so initialize SQLite here.
SqliteRepository.initialize(settings.sqlite_path)

celery.conf.imports = ("app.workers.tasks",)
celery.conf.task_annotations = {
    "app.workers.tasks.execute_migration_job": {"rate_limit": "10/m"}
}
celery.conf.worker_max_tasks_per_child = 100
celery.conf.task_acks_late = True
celery.conf.result_expires = 3600
