from typing import Literal

from pydantic import BaseModel, Field

KnowledgeScopeType = Literal["document", "project"]


class KnowledgeQueryRequest(BaseModel):
    query_text: str = Field(min_length=1, max_length=4000)
    scope_type: KnowledgeScopeType
    scope_id: int = Field(gt=0)
    top_k: int = Field(default=5, ge=1, le=20)
    max_context_chunks: int = Field(default=5, ge=1, le=20)


class DocumentKnowledgeQueryRequest(BaseModel):
    query_text: str = Field(min_length=1, max_length=4000)
    document_id: int = Field(gt=0)
    top_k: int = Field(default=5, ge=1, le=20)
    max_context_chunks: int = Field(default=5, ge=1, le=20)


class ProjectKnowledgeQueryRequest(BaseModel):
    query_text: str = Field(min_length=1, max_length=4000)
    project_id: int = Field(gt=0)
    top_k: int = Field(default=5, ge=1, le=20)
    max_context_chunks: int = Field(default=5, ge=1, le=20)


class KnowledgeQuerySourceResponse(BaseModel):
    document_id: int | None
    project_id: int | None
    workspace_id: int | None
    chunk_index: int | None
    score: float


class KnowledgeQueryResponse(BaseModel):
    query_text: str
    scope_type: str
    scope_id: int
    answer: str
    context_text: str
    chunk_count: int
    sources: list[KnowledgeQuerySourceResponse]
    used_context: bool
