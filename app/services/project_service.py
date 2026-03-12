from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.project_model import Project
from app.models.user_model import User
from app.repositories.project_repository import (
    create_project,
    get_project_by_owner_and_id,
    get_project_by_workspace_and_name,
    list_projects_by_owner,
    update_project,
)
from app.repositories.workspace_repository import get_workspace_by_owner_and_id
from app.schemas.project_schema import ProjectCreateRequest, ProjectUpdateRequest


def create_user_project(db: Session, current_user: User, payload: ProjectCreateRequest) -> Project:
    workspace = get_workspace_by_owner_and_id(db, current_user.id, payload.workspace_id)
    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found",
        )

    existing = get_project_by_workspace_and_name(db, payload.workspace_id, payload.name.strip())
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Project with this name already exists in workspace",
        )

    return create_project(
        db=db,
        owner_id=current_user.id,
        workspace_id=payload.workspace_id,
        name=payload.name.strip(),
        description=payload.description,
    )


def list_user_projects(
    db: Session,
    current_user: User,
    workspace_id: int | None = None,
) -> list[Project]:
    if workspace_id is not None:
        workspace = get_workspace_by_owner_and_id(db, current_user.id, workspace_id)
        if not workspace:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workspace not found",
            )
    return list_projects_by_owner(db, current_user.id, workspace_id)


def get_user_project(db: Session, current_user: User, project_id: int) -> Project:
    project = get_project_by_owner_and_id(db, current_user.id, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
    return project


def update_user_project(
    db: Session,
    current_user: User,
    project_id: int,
    payload: ProjectUpdateRequest,
) -> Project:
    project = get_user_project(db, current_user, project_id)

    if payload.name is not None:
        new_name = payload.name.strip()
        existing = get_project_by_workspace_and_name(db, project.workspace_id, new_name)
        if existing and existing.id != project.id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Project with this name already exists in workspace",
            )
        project.name = new_name

    if payload.description is not None:
        project.description = payload.description

    if payload.is_active is not None:
        project.is_active = payload.is_active

    return update_project(db, project)


def delete_user_project(db: Session, current_user: User, project_id: int) -> None:
    project = get_user_project(db, current_user, project_id)
    project.is_active = False
    update_project(db, project)
