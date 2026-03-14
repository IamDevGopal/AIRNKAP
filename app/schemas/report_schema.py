from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

ReportType = Literal["executive_summary", "research_brief", "risk_report", "custom"]
ReportStatus = Literal["generated"]


class ReportGenerateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    report_type: ReportType
    project_id: int = Field(gt=0)
    source_task_ids: list[int] = Field(min_length=1)
    instruction: str | None = Field(default=None, max_length=4000)


class ReportResponse(BaseModel):
    id: int
    title: str
    report_type: ReportType
    project_id: int
    workspace_id: int
    status: ReportStatus
    instruction: str | None
    source_task_ids: list[int]
    content_text: str
    created_at: datetime
    updated_at: datetime


class ReportDeleteResponse(BaseModel):
    message: str
