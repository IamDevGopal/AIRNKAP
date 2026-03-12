from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models.user_model import User
from app.schemas.auth_schema import AuthTokenResponse, UserRegisterRequest, UserResponse
from app.services.auth_service import (
    authenticate_user,
    create_auth_token_response,
    register_new_user,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(payload: UserRegisterRequest, db: Session = Depends(get_db)) -> UserResponse:
    user = register_new_user(db, payload)
    return UserResponse.model_validate(user)


@router.post("/login", response_model=AuthTokenResponse)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
) -> AuthTokenResponse:
    user = authenticate_user(db, form_data.username, form_data.password)
    return create_auth_token_response(user)


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)) -> UserResponse:
    return UserResponse.model_validate(current_user)
