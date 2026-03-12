from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.auth.jwt_handler import decode_access_token
from app.database import get_db
from app.models.user_model import User
from app.repositories.user_repository import get_user_by_id

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_access_token(token)
    if not payload:
        raise credentials_exception

    subject = payload.get("sub")
    if not subject:
        raise credentials_exception

    try:
        user_id = int(subject)
    except (TypeError, ValueError) as exc:
        raise credentials_exception from exc

    user = get_user_by_id(db, user_id)
    if not user or not user.is_active:
        raise credentials_exception

    return user
