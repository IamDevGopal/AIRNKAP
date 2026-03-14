from __future__ import annotations

from datetime import UTC, datetime
import json
from typing import Literal, cast

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.automation_workflow_model import AutomationWorkflow
from app.models.automation_workflow_run_model import AutomationWorkflowRun
from app.models.user_model import User
from app.repositories.automation_repository import (
    create_automation_workflow,
    create_automation_workflow_run,
    get_automation_workflow_by_owner_and_id,
    list_automation_workflows_by_owner,
    update_automation_workflow,
    update_automation_workflow_run,
)
from app.repositories.document_repository import get_document_by_owner_and_id
from app.repositories.project_repository import get_project_by_owner_and_id
from app.repositories.research_repository import get_research_task_by_owner_and_id
from app.schemas.automation_schema import (
    AutomationWorkflowConfig,
    AutomationWorkflowCreateRequest,
    AutomationWorkflowPauseResponse,
    AutomationWorkflowResponse,
    AutomationWorkflowRunResponse,
    ReportGenerationWorkflowConfig,
    ResearchTaskWorkflowConfig,
    automation_workflow_config_adapter,
)
from app.schemas.knowledge_schema import KnowledgeScopeType
from app.schemas.report_schema import (
    ReportGenerateRequest,
    ReportResponse,
)
from app.schemas.research_task_schema import (
    ResearchTaskCreateRequest,
    ResearchTaskResponse,
    ResearchTaskRunRequest,
)
from app.services.knowledge_service import run_knowledge_query
from app.services.report_service import generate_user_report
from app.services.research_task_service import (
    create_user_research_task,
    run_user_research_task,
)


def create_user_automation_workflow(
    *,
    db: Session,
    current_user: User,
    payload: AutomationWorkflowCreateRequest,
) -> AutomationWorkflowResponse:
    workspace_id, project_id, document_id = _resolve_scope_ids(
        db=db,
        current_user=current_user,
        scope_type=payload.scope_type,
        scope_id=payload.scope_id,
    )
    _validate_workflow_payload(
        db=db,
        current_user=current_user,
        payload=payload,
        project_id=project_id,
    )

    workflow = create_automation_workflow(
        db,
        owner_id=current_user.id,
        workspace_id=workspace_id,
        project_id=project_id,
        document_id=document_id,
        name=payload.name,
        description=payload.description,
        workflow_type=payload.config.workflow_type,
        trigger_type=payload.trigger_type,
        scope_type=payload.scope_type,
        scope_id=payload.scope_id,
        config_json=json.dumps(payload.config.model_dump(mode="json")),
    )
    return _serialize_workflow(workflow)


def list_user_automation_workflows(
    *,
    db: Session,
    current_user: User,
) -> list[AutomationWorkflowResponse]:
    workflows = list_automation_workflows_by_owner(db, current_user.id)
    return [_serialize_workflow(workflow) for workflow in workflows]


def run_user_automation_workflow(
    *,
    db: Session,
    current_user: User,
    workflow_id: int,
) -> AutomationWorkflowRunResponse:
    workflow = _get_owned_workflow(db, current_user.id, workflow_id)
    if workflow.status == "paused":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Paused workflow cannot be run",
        )

    workflow_run = create_automation_workflow_run(
        db,
        workflow_id=workflow.id,
        owner_id=current_user.id,
        started_at=datetime.now(UTC),
    )
    config = _deserialize_workflow_config(workflow.config_json)

    try:
        if config.workflow_type == "knowledge_query":
            query_response = run_knowledge_query(
                db=db,
                current_user=current_user,
                query_text=config.query_text,
                scope_type=cast(KnowledgeScopeType, workflow.scope_type),
                scope_id=workflow.scope_id,
                top_k=config.top_k,
                max_context_chunks=config.max_context_chunks,
            )
            workflow_run.status = "completed"
            workflow_run.result_entity_type = "knowledge_query"
            workflow_run.result_entity_id = None
            workflow_run.result_text = query_response.answer
        elif config.workflow_type == "research_task":
            task_response = _run_research_task_workflow(
                db=db,
                current_user=current_user,
                workflow=workflow,
                config=config,
            )
            workflow_run.status = "completed"
            workflow_run.result_entity_type = "research_task"
            workflow_run.result_entity_id = task_response.id
            workflow_run.result_text = task_response.result_text
        else:
            report_response = _run_report_generation_workflow(
                db=db,
                current_user=current_user,
                workflow=workflow,
                config=config,
            )
            workflow_run.status = "completed"
            workflow_run.result_entity_type = "report"
            workflow_run.result_entity_id = report_response.id
            workflow_run.result_text = report_response.content_text

        workflow_run.error_message = None
        workflow_run.completed_at = datetime.now(UTC)
        workflow_run = update_automation_workflow_run(db, workflow_run)

        workflow.run_count += 1
        workflow.last_run_status = workflow_run.status
        workflow.last_run_at = workflow_run.completed_at
        update_automation_workflow(db, workflow)
    except Exception as exc:
        workflow_run.status = "failed"
        workflow_run.error_message = str(exc)[:3000]
        workflow_run.completed_at = datetime.now(UTC)
        workflow_run = update_automation_workflow_run(db, workflow_run)

        workflow.run_count += 1
        workflow.last_run_status = workflow_run.status
        workflow.last_run_at = workflow_run.completed_at
        update_automation_workflow(db, workflow)
        raise

    return _serialize_workflow_run(workflow_run)


def pause_user_automation_workflow(
    *,
    db: Session,
    current_user: User,
    workflow_id: int,
) -> AutomationWorkflowPauseResponse:
    workflow = _get_owned_workflow(db, current_user.id, workflow_id)
    if workflow.status == "paused":
        return AutomationWorkflowPauseResponse(
            workflow_id=workflow.id,
            status="paused",
            message="Workflow already paused",
        )

    workflow.status = "paused"
    update_automation_workflow(db, workflow)
    return AutomationWorkflowPauseResponse(
        workflow_id=workflow.id,
        status="paused",
        message="Workflow paused successfully",
    )


def _run_research_task_workflow(
    *,
    db: Session,
    current_user: User,
    workflow: AutomationWorkflow,
    config: ResearchTaskWorkflowConfig,
) -> ResearchTaskResponse:
    created_task = create_user_research_task(
        db=db,
        current_user=current_user,
        payload=ResearchTaskCreateRequest(
            task_type=config.task_type,
            title=config.task_title,
            instruction=config.instruction,
            scope_type=cast(KnowledgeScopeType, workflow.scope_type),
            scope_id=workflow.scope_id,
            top_k=config.top_k,
            max_context_chunks=config.max_context_chunks,
        ),
    )
    return run_user_research_task(
        db=db,
        current_user=current_user,
        task_id=created_task.id,
        payload=ResearchTaskRunRequest(
            top_k=config.top_k,
            max_context_chunks=config.max_context_chunks,
        ),
    )


def _run_report_generation_workflow(
    *,
    db: Session,
    current_user: User,
    workflow: AutomationWorkflow,
    config: ReportGenerationWorkflowConfig,
) -> ReportResponse:
    return generate_user_report(
        db=db,
        current_user=current_user,
        payload=ReportGenerateRequest(
            title=config.report_title,
            report_type=config.report_type,
            project_id=workflow.project_id,
            source_task_ids=config.source_task_ids,
            instruction=config.instruction,
        ),
    )


def _get_owned_workflow(db: Session, owner_id: int, workflow_id: int) -> AutomationWorkflow:
    workflow = get_automation_workflow_by_owner_and_id(db, owner_id, workflow_id)
    if workflow is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found",
        )
    return workflow


def _resolve_scope_ids(
    *,
    db: Session,
    current_user: User,
    scope_type: KnowledgeScopeType,
    scope_id: int,
) -> tuple[int, int, int | None]:
    if scope_type == "document":
        document = get_document_by_owner_and_id(db, current_user.id, scope_id)
        if document is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found",
            )
        return document.workspace_id, document.project_id, document.id

    project = get_project_by_owner_and_id(db, current_user.id, scope_id)
    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
    return project.workspace_id, project.id, None


def _validate_workflow_payload(
    *,
    db: Session,
    current_user: User,
    payload: AutomationWorkflowCreateRequest,
    project_id: int,
) -> None:
    if payload.config.workflow_type == "report_generation":
        if payload.scope_type != "project":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Report generation workflows must use project scope",
            )
        for task_id in payload.config.source_task_ids:
            task = get_research_task_by_owner_and_id(db, current_user.id, task_id)
            if task is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Research task {task_id} not found",
                )
            if task.project_id != project_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Research task {task_id} does not belong to the selected project",
                )


def _deserialize_workflow_config(config_json: str) -> AutomationWorkflowConfig:
    return automation_workflow_config_adapter.validate_python(json.loads(config_json))


def _serialize_workflow(workflow: AutomationWorkflow) -> AutomationWorkflowResponse:
    return AutomationWorkflowResponse(
        id=workflow.id,
        name=workflow.name,
        description=workflow.description,
        workflow_type=cast(
            Literal["knowledge_query", "research_task", "report_generation"],
            workflow.workflow_type,
        ),
        trigger_type=cast(Literal["manual", "scheduled", "event"], workflow.trigger_type),
        scope_type=cast(KnowledgeScopeType, workflow.scope_type),
        scope_id=workflow.scope_id,
        workspace_id=workflow.workspace_id,
        project_id=workflow.project_id,
        document_id=workflow.document_id,
        status=cast(Literal["active", "paused"], workflow.status),
        config=_deserialize_workflow_config(workflow.config_json),
        run_count=workflow.run_count,
        last_run_status=cast(
            Literal["running", "completed", "failed"] | None, workflow.last_run_status
        ),
        last_run_at=workflow.last_run_at,
        created_at=workflow.created_at,
        updated_at=workflow.updated_at,
    )


def _serialize_workflow_run(workflow_run: AutomationWorkflowRun) -> AutomationWorkflowRunResponse:
    return AutomationWorkflowRunResponse(
        id=workflow_run.id,
        workflow_id=workflow_run.workflow_id,
        status=cast(Literal["running", "completed", "failed"], workflow_run.status),
        result_entity_type=cast(
            Literal["knowledge_query", "research_task", "report"] | None,
            workflow_run.result_entity_type,
        ),
        result_entity_id=workflow_run.result_entity_id,
        result_text=workflow_run.result_text,
        error_message=workflow_run.error_message,
        started_at=workflow_run.started_at,
        completed_at=workflow_run.completed_at,
        created_at=workflow_run.created_at,
        updated_at=workflow_run.updated_at,
    )
