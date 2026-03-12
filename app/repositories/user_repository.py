from sqlalchemy import select
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
