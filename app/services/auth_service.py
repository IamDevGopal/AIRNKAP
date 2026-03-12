from datetime import timedelta

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.auth.jwt_handler import create_access_token
from app.auth.password_utils import hash_password, verify_password
from app.config import get_settings
from app.models.user_model import User
from app.repositories.user_repository import create_user, get_user_by_email
from app.schemas.auth_schema import AuthTokenResponse, UserRegisterRequest


def register_new_user(db: Session, payload: UserRegisterRequest) -> User:
    existing = get_user_by_email(db, str(payload.email).lower())
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email is already registered",
        )

    return create_user(
        db=db,
        email=str(payload.email).lower(),
        password_hash=hash_password(payload.password),
        full_name=payload.full_name,
    )


def authenticate_user(db: Session, email: str, password: str) -> User:
    user = get_user_by_email(db, email.lower())
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )
    return user


def create_auth_token_response(user: User) -> AuthTokenResponse:
    settings = get_settings()
    expires_delta = timedelta(minutes=settings.access_token_expire_minutes)
    token = create_access_token(
        subject=str(user.id),
        email=user.email,
        expires_delta=expires_delta,
    )
    return AuthTokenResponse(
        access_token=token,
        token_type="bearer",
        expires_in=settings.access_token_expire_minutes * 60,
    )
