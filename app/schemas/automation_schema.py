from __future__ import annotations

from datetime import datetime
from typing import Annotated, Literal

from pydantic import BaseModel, Field, TypeAdapter

from app.schemas.knowledge_schema import KnowledgeScopeType
from app.schemas.report_schema import ReportType
from app.schemas.research_task_schema import ResearchTaskType

AutomationWorkflowType = Literal["knowledge_query", "research_task", "report_generation"]
AutomationTriggerType = Literal["manual", "scheduled", "event"]
AutomationWorkflowStatus = Literal["active", "paused"]
AutomationWorkflowRunStatus = Literal["running", "completed", "failed"]
AutomationResultEntityType = Literal["knowledge_query", "research_task", "report"]


class KnowledgeQueryWorkflowConfig(BaseModel):
    workflow_type: Literal["knowledge_query"]
    query_text: str = Field(min_length=1, max_length=4000)
    top_k: int = Field(default=5, ge=1, le=20)
    max_context_chunks: int = Field(default=5, ge=1, le=20)


class ResearchTaskWorkflowConfig(BaseModel):
    workflow_type: Literal["research_task"]
    task_type: ResearchTaskType
    task_title: str = Field(min_length=1, max_length=255)
    instruction: str = Field(min_length=1, max_length=4000)
    top_k: int = Field(default=5, ge=1, le=20)
    max_context_chunks: int = Field(default=5, ge=1, le=20)


class ReportGenerationWorkflowConfig(BaseModel):
    workflow_type: Literal["report_generation"]
    report_type: ReportType
    report_title: str = Field(min_length=1, max_length=255)
    source_task_ids: list[int] = Field(min_length=1)
    instruction: str | None = Field(default=None, max_length=4000)


AutomationWorkflowConfig = Annotated[
    KnowledgeQueryWorkflowConfig | ResearchTaskWorkflowConfig | ReportGenerationWorkflowConfig,
    Field(discriminator="workflow_type"),
]

automation_workflow_config_adapter: TypeAdapter[AutomationWorkflowConfig] = TypeAdapter(
    AutomationWorkflowConfig
)


class AutomationWorkflowCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=4000)
    trigger_type: AutomationTriggerType = "manual"
    scope_type: KnowledgeScopeType
    scope_id: int = Field(gt=0)
    config: AutomationWorkflowConfig


class AutomationWorkflowResponse(BaseModel):
    id: int
    name: str
    description: str | None
    workflow_type: AutomationWorkflowType
    trigger_type: AutomationTriggerType
    scope_type: KnowledgeScopeType
    scope_id: int
    workspace_id: int
    project_id: int
    document_id: int | None
    status: AutomationWorkflowStatus
    config: AutomationWorkflowConfig
    run_count: int
    last_run_status: AutomationWorkflowRunStatus | None
    last_run_at: datetime | None
    created_at: datetime
    updated_at: datetime


class AutomationWorkflowRunResponse(BaseModel):
    id: int
    workflow_id: int
    status: AutomationWorkflowRunStatus
    result_entity_type: AutomationResultEntityType | None
    result_entity_id: int | None
    result_text: str | None
    error_message: str | None
    started_at: datetime | None
    completed_at: datetime | None
    created_at: datetime
    updated_at: datetime


class AutomationWorkflowPauseResponse(BaseModel):
    workflow_id: int
    status: AutomationWorkflowStatus
    message: str
