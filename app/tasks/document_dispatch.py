import logging

logger = logging.getLogger(__name__)


def enqueue_document_ingestion_job(document_id: int) -> None:
    try:
        from app.tasks.document_ingestion_tasks import ingest_document

        ingest_document.delay(document_id)
    except Exception as exc:
        logger.exception("Failed to enqueue ingestion job for document_id=%s: %s", document_id, exc)
