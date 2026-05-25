from celery import Celery
from backend.app.core.config import settings

celery_app = Celery(
    "finsight_rag",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["backend.app.tasks.ingest_task"]
)

# Optional configurations
celery_app.conf.update(
    task_track_started=True,
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
)
