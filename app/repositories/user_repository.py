from typing import Any

from sqlalchemy import inspect, select, text
from sqlalchemy.orm import Session

from app.models.user_model import User


def get_user_by_email(db: Session, email: str) -> User | None:
    stmt = select(User).where(User.email == email)
    return db.execute(stmt).scalar_one_or_none()


def get_user_by_id(db: Session, user_id: int) -> User | None:
    stmt = select(User).where(User.id == user_id)
    return db.execute(stmt).scalar_one_or_none()


def create_user(
    db: Session,
    email: str,
    password_hash: str,
    full_name: str | None = None,
) -> User:
    user = User(
        email=email,
        password_hash=password_hash,
        full_name=full_name,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def update_user_profile(db: Session, user: User, full_name: str | None) -> User:
    user.full_name = full_name
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def update_user_password(db: Session, user: User, new_password_hash: str) -> User:
    user.password_hash = new_password_hash
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def deactivate_user(db: Session, user: User) -> None:
    user.is_active = False
    db.add(user)
    db.commit()


def get_user_stats(db: Session, user_id: int) -> dict[str, int]:
    # Single-user phase: return scoped counts where table exists.
    # If future tables/columns are not yet migrated, fallback safely to 0.
    inspector = inspect(db.get_bind())

    def count_if_exists(table_name: str, owner_column: str) -> int:
        if not inspector.has_table(table_name):
            return 0
        query = text(f"SELECT COUNT(1) FROM {table_name} WHERE {owner_column} = :user_id")
        result: Any = db.execute(query, {"user_id": user_id}).scalar()
        return int(result or 0)

    return {
        "workspace_count": count_if_exists("workspaces", "owner_id"),
        "project_count": count_if_exists("projects", "owner_id"),
        "document_count": count_if_exists("documents", "owner_id"),
        "research_task_count": count_if_exists("research_tasks", "owner_id"),
        "report_count": count_if_exists("reports", "owner_id"),
    }
