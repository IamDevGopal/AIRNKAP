from datetime import UTC, datetime
import hashlib
from typing import Any

from app.config import get_settings
from app.database import SessionLocal
from app.repositories.document_repository import (
    get_document_by_id,
    replace_document_chunks,
    update_document_ingestion_fields,
)
from app.services.chunking_service import chunk_text_by_tokens
from app.services.embedding_service import generate_embeddings
from app.services.file_parser_service import extract_text_from_file
from app.services.vector_index_service import upsert_document_vectors
from app.tasks.celery_app import celery_app

settings = get_settings()


@celery_app.task(
    bind=True,
    name="document.ingest",
    queue=settings.celery_ingestion_queue,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_jitter=True,
    retry_kwargs={"max_retries": settings.celery_ingestion_max_retries},
)
def ingest_document(self: Any, document_id: int) -> None:
    db = SessionLocal()
    document = None

    try:
        document = get_document_by_id(db, document_id)
        if not document:
            return

        update_document_ingestion_fields(
            db=db,
            document=document,
            ingestion_status="processing",
            ingestion_error=None,
            ingestion_started_at=datetime.now(UTC),
            ingestion_completed_at=None,
        )

        parsed_text = extract_text_from_file(document.file_path)
        if not parsed_text.strip():
            raise ValueError("No parseable text extracted from document")

        chunks = chunk_text_by_tokens(
            parsed_text,
            chunk_size_tokens=settings.chunk_size_tokens,
            chunk_overlap_tokens=settings.chunk_overlap_tokens,
            model_name=settings.embedding_model_name,
        )

        replace_document_chunks(
            db=db,
            document_id=document.id,
            chunks=[(chunk.chunk_index, chunk.chunk_text, chunk.token_count) for chunk in chunks],
        )

        chunk_texts = [chunk.chunk_text for chunk in chunks]
        embeddings = generate_embeddings(chunk_texts)
        upsert_document_vectors(
            document=document,
            chunks=chunks,
            embeddings=embeddings,
        )

        content_hash = hashlib.sha256(parsed_text.encode("utf-8")).hexdigest()
        update_document_ingestion_fields(
            db=db,
            document=document,
            ingestion_status="ready",
            ingestion_error=None,
            ingestion_started_at=document.ingestion_started_at,
            ingestion_completed_at=datetime.now(UTC),
            chunk_count=len(chunks),
            embedding_model=settings.embedding_model_name,
            embedding_version=settings.embedding_model_version,
            content_hash=content_hash,
        )
    except Exception as exc:
        if document:
            update_document_ingestion_fields(
                db=db,
                document=document,
                ingestion_status="failed",
                ingestion_error=str(exc)[:3000],
                ingestion_started_at=document.ingestion_started_at,
                ingestion_completed_at=datetime.now(UTC),
            )
        raise
    finally:
        db.close()
