from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models.user_model import User
from app.schemas.workspace_schema import (
    WorkspaceCreateRequest,
    WorkspaceDeleteResponse,
    WorkspaceResponse,
    WorkspaceUpdateRequest,
)
from app.services.workspace_service import (
    create_user_workspace,
    delete_user_workspace,
    get_user_workspace,
    list_user_workspaces,
    update_user_workspace,
)

router = APIRouter(prefix="/workspaces", tags=["workspaces"])


@router.post("", response_model=WorkspaceResponse, status_code=status.HTTP_201_CREATED)
def create_workspace(
    payload: WorkspaceCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> WorkspaceResponse:
    workspace = create_user_workspace(db, current_user, payload)
    return WorkspaceResponse.model_validate(workspace)


@router.get("", response_model=list[WorkspaceResponse])
def list_workspaces(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[WorkspaceResponse]:
    workspaces = list_user_workspaces(db, current_user)
    return [WorkspaceResponse.model_validate(workspace) for workspace in workspaces]


@router.get("/{workspace_id}", response_model=WorkspaceResponse)
def get_workspace(
    workspace_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> WorkspaceResponse:
    workspace = get_user_workspace(db, current_user, workspace_id)
    return WorkspaceResponse.model_validate(workspace)


@router.patch("/{workspace_id}", response_model=WorkspaceResponse)
def update_workspace(
    workspace_id: int,
    payload: WorkspaceUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> WorkspaceResponse:
    workspace = update_user_workspace(db, current_user, workspace_id, payload)
    return WorkspaceResponse.model_validate(workspace)


@router.delete("/{workspace_id}", response_model=WorkspaceDeleteResponse)
def delete_workspace(
    workspace_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> WorkspaceDeleteResponse:
    delete_user_workspace(db, current_user, workspace_id)
    return WorkspaceDeleteResponse(message="Workspace deactivated successfully")
