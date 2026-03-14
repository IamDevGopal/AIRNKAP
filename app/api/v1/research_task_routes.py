from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models.user_model import User
from app.schemas.research_task_schema import (
    ResearchTaskCancelResponse,
    ResearchTaskCreateRequest,
    ResearchTaskResponse,
    ResearchTaskRunRequest,
)
from app.services.research_task_service import (
    cancel_user_research_task,
    create_user_research_task,
    get_user_research_task,
    list_user_research_tasks,
    run_user_research_task,
)

router = APIRouter(prefix="/research-tasks", tags=["research-tasks"])


@router.post("", response_model=ResearchTaskResponse)
def create_research_task(
    payload: ResearchTaskCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ResearchTaskResponse:
    return create_user_research_task(
        db=db,
        current_user=current_user,
        payload=payload,
    )


@router.get("", response_model=list[ResearchTaskResponse])
def list_research_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[ResearchTaskResponse]:
    return list_user_research_tasks(
        db=db,
        current_user=current_user,
    )


@router.get("/{task_id}", response_model=ResearchTaskResponse)
def get_research_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ResearchTaskResponse:
    return get_user_research_task(
        db=db,
        current_user=current_user,
        task_id=task_id,
    )


@router.post("/{task_id}/run", response_model=ResearchTaskResponse)
def run_research_task(
    task_id: int,
    payload: ResearchTaskRunRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ResearchTaskResponse:
    return run_user_research_task(
        db=db,
        current_user=current_user,
        task_id=task_id,
        payload=payload,
    )


@router.post("/{task_id}/cancel", response_model=ResearchTaskCancelResponse)
def cancel_research_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ResearchTaskCancelResponse:
    return cancel_user_research_task(
        db=db,
        current_user=current_user,
        task_id=task_id,
    )
