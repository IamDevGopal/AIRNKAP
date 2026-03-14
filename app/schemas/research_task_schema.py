from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.knowledge_schema import KnowledgeScopeType

ResearchTaskType = Literal[
    "summary",
    "compare",
    "risk_extraction",
    "timeline",
    "action_items",
    "custom",
]
ResearchTaskStatus = Literal["pending", "running", "completed", "failed", "cancelled"]


class ResearchTaskCreateRequest(BaseModel):
    task_type: ResearchTaskType
    title: str = Field(min_length=1, max_length=255)
    instruction: str = Field(min_length=1, max_length=4000)
    scope_type: KnowledgeScopeType
    scope_id: int = Field(gt=0)
    top_k: int = Field(default=5, ge=1, le=20)
    max_context_chunks: int = Field(default=5, ge=1, le=20)


class ResearchTaskRunRequest(BaseModel):
    top_k: int = Field(default=5, ge=1, le=20)
    max_context_chunks: int = Field(default=5, ge=1, le=20)


class ResearchTaskSourceResponse(BaseModel):
    document_id: int | None
    project_id: int | None
    workspace_id: int | None
    chunk_index: int | None
    score: float


class ResearchTaskResponse(BaseModel):
    id: int
    task_type: ResearchTaskType
    title: str
    instruction: str
    scope_type: KnowledgeScopeType
    scope_id: int
    workspace_id: int
    project_id: int
    document_id: int | None
    status: ResearchTaskStatus
    result_text: str | None
    result_chunk_count: int
    error_message: str | None
    created_at: datetime
    updated_at: datetime
    started_at: datetime | None
    completed_at: datetime | None
    cancelled_at: datetime | None
    sources: list[ResearchTaskSourceResponse]


class ResearchTaskCancelResponse(BaseModel):
    message: str
