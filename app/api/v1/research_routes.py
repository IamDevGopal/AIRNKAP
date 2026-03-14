from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models.user_model import User
from app.schemas.research_schema import (
    ChatMessageRequest,
    ChatSessionDeleteResponse,
    ChatSessionDetailResponse,
    ChatSessionSummaryResponse,
    ChatTurnResponse,
)
from app.services.research_service import (
    delete_user_chat_session,
    get_chat_session_detail,
    list_user_chat_sessions,
    send_chat_message,
)

router = APIRouter(prefix="/research", tags=["research"])


@router.post("/chat", response_model=ChatTurnResponse)
def chat_with_research_context(
    payload: ChatMessageRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ChatTurnResponse:
    return send_chat_message(
        db=db,
        current_user=current_user,
        payload=payload,
    )


@router.get("/chat/sessions", response_model=list[ChatSessionSummaryResponse])
def list_chat_sessions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[ChatSessionSummaryResponse]:
    return list_user_chat_sessions(
        db=db,
        current_user=current_user,
    )


@router.get("/chat/sessions/{session_id}", response_model=ChatSessionDetailResponse)
def get_chat_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ChatSessionDetailResponse:
    return get_chat_session_detail(
        db=db,
        current_user=current_user,
        session_id=session_id,
    )


@router.delete("/chat/sessions/{session_id}", response_model=ChatSessionDeleteResponse)
def remove_chat_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ChatSessionDeleteResponse:
    return delete_user_chat_session(
        db=db,
        current_user=current_user,
        session_id=session_id,
    )
