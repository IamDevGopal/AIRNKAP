from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.auth.password_utils import hash_password, verify_password
from app.models.user_model import User
from app.repositories.user_repository import (
    deactivate_user,
    get_user_stats,
    update_user_password,
    update_user_profile,
)
from app.schemas.user_schema import (
    ChangePasswordRequest,
    UserProfileUpdateRequest,
    UserStatsResponse,
)


def update_current_user_profile(
    db: Session,
    user: User,
    payload: UserProfileUpdateRequest,
) -> User:
    return update_user_profile(db, user, payload.full_name)


def change_current_user_password(
    db: Session,
    user: User,
    payload: ChangePasswordRequest,
) -> None:
    if not verify_password(payload.current_password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect",
        )
    if payload.current_password == payload.new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be different from current password",
        )
    update_user_password(db, user, hash_password(payload.new_password))


def deactivate_current_user(db: Session, user: User) -> None:
    deactivate_user(db, user)


def get_current_user_stats(db: Session, user: User) -> UserStatsResponse:
    stats = get_user_stats(db, user.id)
    return UserStatsResponse(**stats)
