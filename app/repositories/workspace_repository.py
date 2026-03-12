from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.workspace_model import Workspace


def list_workspaces_by_owner(db: Session, owner_id: int) -> list[Workspace]:
    stmt = select(Workspace).where(Workspace.owner_id == owner_id).order_by(Workspace.id.desc())
    return list(db.execute(stmt).scalars().all())


def get_workspace_by_owner_and_id(
    db: Session, owner_id: int, workspace_id: int
) -> Workspace | None:
    stmt = select(Workspace).where(
        Workspace.owner_id == owner_id,
        Workspace.id == workspace_id,
    )
    return db.execute(stmt).scalar_one_or_none()


def get_workspace_by_owner_and_name(db: Session, owner_id: int, name: str) -> Workspace | None:
    stmt = select(Workspace).where(
        Workspace.owner_id == owner_id,
        Workspace.name == name,
    )
    return db.execute(stmt).scalar_one_or_none()


def create_workspace(
    db: Session,
    owner_id: int,
    name: str,
    description: str | None = None,
) -> Workspace:
    workspace = Workspace(
        owner_id=owner_id,
        name=name,
        description=description,
        is_active=True,
    )
    db.add(workspace)
    db.commit()
    db.refresh(workspace)
    return workspace


def update_workspace(db: Session, workspace: Workspace) -> Workspace:
    db.add(workspace)
    db.commit()
    db.refresh(workspace)
    return workspace
