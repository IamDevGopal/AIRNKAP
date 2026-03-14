from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models.user_model import User
from app.schemas.automation_schema import (
    AutomationWorkflowCreateRequest,
    AutomationWorkflowPauseResponse,
    AutomationWorkflowResponse,
    AutomationWorkflowRunResponse,
)
from app.services.automation_service import (
    create_user_automation_workflow,
    list_user_automation_workflows,
    pause_user_automation_workflow,
    run_user_automation_workflow,
)

router = APIRouter(prefix="/automation/workflows", tags=["automation"])


@router.post("", response_model=AutomationWorkflowResponse, status_code=status.HTTP_201_CREATED)
def create_workflow(
    payload: AutomationWorkflowCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AutomationWorkflowResponse:
    return create_user_automation_workflow(
        db=db,
        current_user=current_user,
        payload=payload,
    )


@router.get("", response_model=list[AutomationWorkflowResponse])
def list_workflows(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[AutomationWorkflowResponse]:
    return list_user_automation_workflows(
        db=db,
        current_user=current_user,
    )


@router.post("/{workflow_id}/run", response_model=AutomationWorkflowRunResponse)
def run_workflow(
    workflow_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AutomationWorkflowRunResponse:
    return run_user_automation_workflow(
        db=db,
        current_user=current_user,
        workflow_id=workflow_id,
    )


@router.post("/{workflow_id}/pause", response_model=AutomationWorkflowPauseResponse)
def pause_workflow(
    workflow_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AutomationWorkflowPauseResponse:
    return pause_user_automation_workflow(
        db=db,
        current_user=current_user,
        workflow_id=workflow_id,
    )
