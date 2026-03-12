from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user_model import User
from app.models.workspace_model import Workspace
from app.repositories.workspace_repository import (
    create_workspace,
    get_workspace_by_owner_and_id,
    get_workspace_by_owner_and_name,
    list_workspaces_by_owner,
    update_workspace,
)
from app.schemas.workspace_schema import WorkspaceCreateRequest, WorkspaceUpdateRequest


def create_user_workspace(
    db: Session, current_user: User, payload: WorkspaceCreateRequest
) -> Workspace:
    existing = get_workspace_by_owner_and_name(db, current_user.id, payload.name.strip())
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Workspace with this name already exists",
        )
    return create_workspace(
        db=db,
        owner_id=current_user.id,
        name=payload.name.strip(),
        description=payload.description,
    )


def list_user_workspaces(db: Session, current_user: User) -> list[Workspace]:
    return list_workspaces_by_owner(db, current_user.id)


def get_user_workspace(db: Session, current_user: User, workspace_id: int) -> Workspace:
    workspace = get_workspace_by_owner_and_id(db, current_user.id, workspace_id)
    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found",
        )
    return workspace


def update_user_workspace(
    db: Session,
    current_user: User,
    workspace_id: int,
    payload: WorkspaceUpdateRequest,
) -> Workspace:
    workspace = get_user_workspace(db, current_user, workspace_id)

    if payload.name is not None:
        new_name = payload.name.strip()
        existing = get_workspace_by_owner_and_name(db, current_user.id, new_name)
        if existing and existing.id != workspace.id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Workspace with this name already exists",
            )
        workspace.name = new_name

    if payload.description is not None:
        workspace.description = payload.description

    if payload.is_active is not None:
        workspace.is_active = payload.is_active

    return update_workspace(db, workspace)


def delete_user_workspace(db: Session, current_user: User, workspace_id: int) -> None:
    workspace = get_user_workspace(db, current_user, workspace_id)
    workspace.is_active = False
    update_workspace(db, workspace)
