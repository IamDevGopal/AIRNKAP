from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, model_validator

from app.schemas.knowledge_schema import KnowledgeScopeType

ChatRole = Literal["user", "assistant"]


class ChatMessageRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    session_id: int | None = Field(default=None, gt=0)
    scope_type: KnowledgeScopeType | None = None
    scope_id: int | None = Field(default=None, gt=0)
    top_k: int = Field(default=5, ge=1, le=20)
    max_context_chunks: int = Field(default=5, ge=1, le=20)

    @model_validator(mode="after")
    def validate_scope_input(self) -> "ChatMessageRequest":
        if self.session_id is None and (self.scope_type is None or self.scope_id is None):
            raise ValueError("scope_type and scope_id are required when session_id is not provided")
        return self


class ChatMessageSourceResponse(BaseModel):
    document_id: int | None
    project_id: int | None
    workspace_id: int | None
    chunk_index: int | None
    score: float


class ChatMessageResponse(BaseModel):
    id: int
    role: ChatRole
    content: str
    context_text: str | None = None
    chunk_count: int
    used_context: bool
    sources: list[ChatMessageSourceResponse]
    created_at: datetime


class ChatSessionSummaryResponse(BaseModel):
    id: int
    title: str
    scope_type: KnowledgeScopeType
    scope_id: int
    workspace_id: int
    project_id: int
    document_id: int | None
    created_at: datetime
    updated_at: datetime


class ChatSessionDetailResponse(BaseModel):
    session: ChatSessionSummaryResponse
    messages: list[ChatMessageResponse]


class ChatTurnResponse(BaseModel):
    created_new_session: bool
    session: ChatSessionSummaryResponse
    user_message: ChatMessageResponse
    assistant_message: ChatMessageResponse


class ChatSessionDeleteResponse(BaseModel):
    message: str
