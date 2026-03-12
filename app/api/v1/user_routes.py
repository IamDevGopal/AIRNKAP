from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models.user_model import User
from app.schemas.user_schema import (
    ChangePasswordRequest,
    UserDeactivateResponse,
    UserProfileResponse,
    UserProfileUpdateRequest,
    UserStatsResponse,
)
from app.services.user_service import (
    change_current_user_password,
    deactivate_current_user,
    get_current_user_stats,
    update_current_user_profile,
)

router = APIRouter(prefix="/users", tags=["users"])


@router.patch("/me", response_model=UserProfileResponse)
def update_me(
    payload: UserProfileUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UserProfileResponse:
    user = update_current_user_profile(db, current_user, payload)
    return UserProfileResponse.model_validate(user)


@router.patch("/me/password", status_code=status.HTTP_204_NO_CONTENT)
def update_password(
    payload: ChangePasswordRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    change_current_user_password(db, current_user, payload)


@router.get("/me/stats", response_model=UserStatsResponse)
def get_me_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UserStatsResponse:
    return get_current_user_stats(db, current_user)


@router.delete("/me", response_model=UserDeactivateResponse)
def deactivate_me(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UserDeactivateResponse:
    deactivate_current_user(db, current_user)
    return UserDeactivateResponse(message="Account deactivated successfully")
