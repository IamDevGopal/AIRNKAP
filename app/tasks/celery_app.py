from celery import Celery

from app.config import get_settings

settings = get_settings()

celery_app = Celery(
    "airnkap",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["app.tasks.document_ingestion_tasks"],
)

celery_app.conf.update(
    task_default_queue=settings.celery_ingestion_queue,
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
)
