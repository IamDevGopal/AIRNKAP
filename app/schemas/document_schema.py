from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

DocumentSourceType = Literal["manual", "url", "file"]
DocumentStatus = Literal["active", "archived", "deleted"]


class DocumentCreateRequest(BaseModel):
    project_id: int
    title: str = Field(min_length=1, max_length=255)
    source_type: DocumentSourceType = "manual"
    source_uri: str | None = Field(default=None, max_length=1000)
    content_text: str | None = None


class DocumentUpdateRequest(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    source_type: DocumentSourceType | None = None
    source_uri: str | None = Field(default=None, max_length=1000)
    content_text: str | None = None
    status: DocumentStatus | None = None


class DocumentResponse(BaseModel):
    id: int
    owner_id: int
    workspace_id: int
    project_id: int
    title: str
    source_type: str
    source_uri: str | None
    content_text: str | None
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class DocumentDeleteResponse(BaseModel):
    message: str
