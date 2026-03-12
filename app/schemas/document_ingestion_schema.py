from datetime import datetime
from typing import Literal

from pydantic import BaseModel

DocumentIngestionStatus = Literal["queued", "processing", "ready", "failed"]


class DocumentIngestionStatusResponse(BaseModel):
    document_id: int
    ingestion_status: DocumentIngestionStatus
    ingestion_error: str | None
    ingestion_started_at: datetime | None
    ingestion_completed_at: datetime | None
    chunk_count: int
    embedding_model: str | None
    embedding_version: str | None
    updated_at: datetime


class DocumentChunkResponse(BaseModel):
    id: int
    document_id: int
    chunk_index: int
    chunk_text: str
    token_count: int | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
