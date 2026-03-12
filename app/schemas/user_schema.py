from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class UserProfileResponse(BaseModel):
    id: int
    email: EmailStr
    full_name: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class UserProfileUpdateRequest(BaseModel):
    full_name: str | None = Field(default=None, max_length=255)


class ChangePasswordRequest(BaseModel):
    current_password: str = Field(min_length=8, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)


class UserStatsResponse(BaseModel):
    workspace_count: int
    project_count: int
    document_count: int
    research_task_count: int
    report_count: int


class UserDeactivateResponse(BaseModel):
    message: str
