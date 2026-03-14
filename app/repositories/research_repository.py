from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.research_task_model import ResearchTask


def create_research_task(
    db: Session,
    *,
    owner_id: int,
    workspace_id: int,
    project_id: int,
    document_id: int | None,
    task_type: str,
    title: str,
    instruction: str,
    scope_type: str,
    scope_id: int,
) -> ResearchTask:
    task = ResearchTask(
        owner_id=owner_id,
        workspace_id=workspace_id,
        project_id=project_id,
        document_id=document_id,
        task_type=task_type,
        title=title,
        instruction=instruction,
        scope_type=scope_type,
        scope_id=scope_id,
        status="pending",
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def list_research_tasks_by_owner(
    db: Session,
    owner_id: int,
    *,
    limit: int = 50,
    offset: int = 0,
) -> list[ResearchTask]:
    stmt = (
        select(ResearchTask)
        .where(ResearchTask.owner_id == owner_id)
        .order_by(ResearchTask.created_at.desc(), ResearchTask.id.desc())
        .limit(limit)
        .offset(offset)
    )
    return list(db.execute(stmt).scalars().all())


def get_research_task_by_owner_and_id(
    db: Session,
    owner_id: int,
    task_id: int,
) -> ResearchTask | None:
    stmt = select(ResearchTask).where(
        ResearchTask.owner_id == owner_id,
        ResearchTask.id == task_id,
    )
    return db.execute(stmt).scalar_one_or_none()


def update_research_task(db: Session, task: ResearchTask) -> ResearchTask:
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def set_research_task_running(
    db: Session,
    task: ResearchTask,
    *,
    started_at: datetime,
) -> ResearchTask:
    task.status = "running"
    task.started_at = started_at
    task.completed_at = None
    task.cancelled_at = None
    task.error_message = None
    return update_research_task(db, task)


def set_research_task_completed(
    db: Session,
    task: ResearchTask,
    *,
    result_text: str,
    result_sources_json: str,
    result_chunk_count: int,
    completed_at: datetime,
) -> ResearchTask:
    task.status = "completed"
    task.result_text = result_text
    task.result_sources_json = result_sources_json
    task.result_chunk_count = result_chunk_count
    task.completed_at = completed_at
    task.error_message = None
    return update_research_task(db, task)


def set_research_task_failed(
    db: Session,
    task: ResearchTask,
    *,
    error_message: str,
    completed_at: datetime,
) -> ResearchTask:
    task.status = "failed"
    task.error_message = error_message
    task.completed_at = completed_at
    return update_research_task(db, task)


def set_research_task_cancelled(
    db: Session,
    task: ResearchTask,
    *,
    cancelled_at: datetime,
) -> ResearchTask:
    task.status = "cancelled"
    task.cancelled_at = cancelled_at
    return update_research_task(db, task)
