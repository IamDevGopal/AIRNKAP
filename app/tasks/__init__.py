from app.tasks.celery_app import celery_app
from app.tasks.document_ingestion_tasks import ingest_document

__all__ = ["celery_app", "ingest_document"]
