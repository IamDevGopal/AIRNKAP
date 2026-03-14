from datetime import UTC, datetime
import json
from typing import cast

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.ai.llm.wrappers.chat import generate_contextual_response
from app.ai.rag.retrieval import (
    RetrievalRequest,
    RetrievalScope,
    run_retrieval_pipeline,
)
from app.ai.rag.retrieval.context_builder import ContextSource
from app.models.research_task_model import ResearchTask
from app.models.user_model import User
from app.repositories.document_repository import get_document_by_owner_and_id
from app.repositories.project_repository import get_project_by_owner_and_id
from app.repositories.research_repository import (
    create_research_task,
    get_research_task_by_owner_and_id,
    list_research_tasks_by_owner,
    set_research_task_cancelled,
    set_research_task_completed,
    set_research_task_failed,
    set_research_task_running,
)
from app.schemas.knowledge_schema import KnowledgeScopeType
from app.schemas.research_task_schema import (
    ResearchTaskCancelResponse,
    ResearchTaskCreateRequest,
    ResearchTaskResponse,
    ResearchTaskRunRequest,
    ResearchTaskSourceResponse,
    ResearchTaskStatus,
    ResearchTaskType,
)


def create_user_research_task(
    *,
    db: Session,
    current_user: User,
    payload: ResearchTaskCreateRequest,
) -> ResearchTaskResponse:
    workspace_id, project_id, document_id = _resolve_scope_ids(
        db=db,
        current_user=current_user,
        scope_type=payload.scope_type,
        scope_id=payload.scope_id,
    )
    task = create_research_task(
        db,
        owner_id=current_user.id,
        workspace_id=workspace_id,
        project_id=project_id,
        document_id=document_id,
        task_type=payload.task_type,
        title=payload.title,
        instruction=payload.instruction,
        scope_type=payload.scope_type,
        scope_id=payload.scope_id,
    )
    return _serialize_task(task)


def list_user_research_tasks(
    *,
    db: Session,
    current_user: User,
) -> list[ResearchTaskResponse]:
    tasks = list_research_tasks_by_owner(db, current_user.id)
    return [_serialize_task(task) for task in tasks]


def get_user_research_task(
    *,
    db: Session,
    current_user: User,
    task_id: int,
) -> ResearchTaskResponse:
    task = _get_owned_task(db, current_user.id, task_id)
    return _serialize_task(task)


def run_user_research_task(
    *,
    db: Session,
    current_user: User,
    task_id: int,
    payload: ResearchTaskRunRequest,
) -> ResearchTaskResponse:
    task = _get_owned_task(db, current_user.id, task_id)
    if task.status == "running":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Research task is already running",
        )
    if task.status == "cancelled":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cancelled research task cannot be run",
        )

    task = set_research_task_running(db, task, started_at=datetime.now(UTC))
    try:
        retrieval_response = run_retrieval_pipeline(
            RetrievalRequest(
                query_text=task.instruction,
                scope=RetrievalScope(
                    scope_type=cast(KnowledgeScopeType, task.scope_type),
                    scope_id=task.scope_id,
                ),
                top_k=payload.top_k,
                max_context_chunks=payload.max_context_chunks,
            )
        )
        context_text = retrieval_response.context.context_text.strip()
        if not context_text:
            result_text = "No relevant context was found in the selected knowledge scope."
        else:
            result_text = generate_contextual_response(
                system_instruction=_build_system_instruction(
                    cast(ResearchTaskType, task.task_type)
                ),
                user_instruction=_build_user_instruction(task.title, task.instruction),
                context_text=context_text,
                response_instruction=_build_response_instruction(
                    cast(ResearchTaskType, task.task_type)
                ),
            )

        task = set_research_task_completed(
            db,
            task,
            result_text=result_text,
            result_sources_json=json.dumps(
                [_serialize_source(source) for source in retrieval_response.context.sources]
            ),
            result_chunk_count=retrieval_response.context.chunk_count,
            completed_at=datetime.now(UTC),
        )
    except Exception as exc:
        task = set_research_task_failed(
            db,
            task,
            error_message=str(exc)[:3000],
            completed_at=datetime.now(UTC),
        )
        raise

    return _serialize_task(task)


def cancel_user_research_task(
    *,
    db: Session,
    current_user: User,
    task_id: int,
) -> ResearchTaskCancelResponse:
    task = _get_owned_task(db, current_user.id, task_id)
    if task.status == "running":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Synchronous running tasks cannot be cancelled",
        )
    if task.status == "completed":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Completed research task cannot be cancelled",
        )
    if task.status == "failed":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Failed research task cannot be cancelled",
        )
    if task.status == "cancelled":
        return ResearchTaskCancelResponse(message="Research task already cancelled")

    set_research_task_cancelled(db, task, cancelled_at=datetime.now(UTC))
    return ResearchTaskCancelResponse(message="Research task cancelled successfully")


def _get_owned_task(db: Session, owner_id: int, task_id: int) -> ResearchTask:
    task = get_research_task_by_owner_and_id(db, owner_id, task_id)
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Research task not found",
        )
    return task


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


def _serialize_task(task: ResearchTask) -> ResearchTaskResponse:
    sources = []
    if task.result_sources_json:
        sources = [
            ResearchTaskSourceResponse.model_validate(item)
            for item in json.loads(task.result_sources_json)
        ]
    return ResearchTaskResponse(
        id=task.id,
        task_type=cast(ResearchTaskType, task.task_type),
        title=task.title,
        instruction=task.instruction,
        scope_type=cast(KnowledgeScopeType, task.scope_type),
        scope_id=task.scope_id,
        workspace_id=task.workspace_id,
        project_id=task.project_id,
        document_id=task.document_id,
        status=cast(ResearchTaskStatus, task.status),
        result_text=task.result_text,
        result_chunk_count=task.result_chunk_count,
        error_message=task.error_message,
        created_at=task.created_at,
        updated_at=task.updated_at,
        started_at=task.started_at,
        completed_at=task.completed_at,
        cancelled_at=task.cancelled_at,
        sources=sources,
    )


def _serialize_source(source: ContextSource) -> dict[str, int | float | None]:
    return {
        "document_id": source.document_id,
        "project_id": source.project_id,
        "workspace_id": source.workspace_id,
        "chunk_index": source.chunk_index,
        "score": source.score,
    }


def _build_system_instruction(task_type: ResearchTaskType) -> str:
    task_prompts: dict[ResearchTaskType, str] = {
        "summary": (
            "You produce grounded document or project summaries using only the provided context."
        ),
        "compare": (
            "You compare evidence found in the provided context only. Be explicit about similarities, differences, and missing evidence."
        ),
        "risk_extraction": (
            "You identify risks strictly from the provided context. Group related risks and avoid unsupported claims."
        ),
        "timeline": ("You extract and organize timeline events using only the provided context."),
        "action_items": (
            "You extract concrete action items and responsibilities strictly from the provided context."
        ),
        "custom": ("You complete the requested research task using only the provided context."),
    }
    return task_prompts[task_type]


def _build_response_instruction(task_type: ResearchTaskType) -> str:
    task_outputs: dict[ResearchTaskType, str] = {
        "summary": "Return a concise structured summary with headings and bullets where useful.",
        "compare": "Return a comparison with clear sections: overlaps, differences, and gaps.",
        "risk_extraction": "Return a risk list with severity hints when the context supports them.",
        "timeline": "Return an ordered timeline with dates or relative sequence when available.",
        "action_items": "Return a clear action-items list with owners or context if available.",
        "custom": "Return a concise grounded research output.",
    }
    return task_outputs[task_type]


def _build_user_instruction(title: str, instruction: str) -> str:
    return f"Research Task Title:\n{title}\n\nInstruction:\n{instruction}"
