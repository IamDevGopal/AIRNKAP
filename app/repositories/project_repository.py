from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.project_model import Project


def list_projects_by_owner(
    db: Session, owner_id: int, workspace_id: int | None = None
) -> list[Project]:
    stmt = select(Project).where(Project.owner_id == owner_id)
    if workspace_id is not None:
        stmt = stmt.where(Project.workspace_id == workspace_id)
    stmt = stmt.order_by(Project.id.desc())
    return list(db.execute(stmt).scalars().all())


def get_project_by_owner_and_id(db: Session, owner_id: int, project_id: int) -> Project | None:
    stmt = select(Project).where(
        Project.owner_id == owner_id,
        Project.id == project_id,
    )
    return db.execute(stmt).scalar_one_or_none()


def get_project_by_workspace_and_name(
    db: Session,
    workspace_id: int,
    name: str,
) -> Project | None:
    stmt = select(Project).where(
        Project.workspace_id == workspace_id,
        Project.name == name,
    )
    return db.execute(stmt).scalar_one_or_none()


def create_project(
    db: Session,
    owner_id: int,
    workspace_id: int,
    name: str,
    description: str | None = None,
) -> Project:
    project = Project(
        owner_id=owner_id,
        workspace_id=workspace_id,
        name=name,
        description=description,
        is_active=True,
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


def update_project(db: Session, project: Project) -> Project:
    db.add(project)
    db.commit()
    db.refresh(project)
    return project
