from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.chat_message_model import ChatMessage
from app.models.chat_session_model import ChatSession


def list_chat_sessions_by_owner(
    db: Session,
    owner_id: int,
    limit: int = 50,
    offset: int = 0,
) -> list[ChatSession]:
    stmt = (
        select(ChatSession)
        .where(ChatSession.owner_id == owner_id)
        .order_by(ChatSession.updated_at.desc(), ChatSession.id.desc())
        .limit(limit)
        .offset(offset)
    )
    return list(db.execute(stmt).scalars().all())


def get_chat_session_by_owner_and_id(
    db: Session,
    owner_id: int,
    session_id: int,
) -> ChatSession | None:
    stmt = select(ChatSession).where(
        ChatSession.owner_id == owner_id,
        ChatSession.id == session_id,
    )
    return db.execute(stmt).scalar_one_or_none()


def create_chat_session(
    db: Session,
    *,
    owner_id: int,
    workspace_id: int,
    project_id: int,
    document_id: int | None,
    scope_type: str,
    scope_id: int,
    title: str,
) -> ChatSession:
    session = ChatSession(
        owner_id=owner_id,
        workspace_id=workspace_id,
        project_id=project_id,
        document_id=document_id,
        scope_type=scope_type,
        scope_id=scope_id,
        title=title,
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def delete_chat_session(db: Session, session: ChatSession) -> None:
    db.delete(session)
    db.commit()


def list_chat_messages_by_session_id(db: Session, session_id: int) -> list[ChatMessage]:
    stmt = (
        select(ChatMessage)
        .where(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.id.asc())
    )
    return list(db.execute(stmt).scalars().all())


def list_recent_chat_messages(
    db: Session,
    session_id: int,
    limit: int,
) -> list[ChatMessage]:
    stmt = (
        select(ChatMessage)
        .where(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.id.desc())
        .limit(limit)
    )
    messages = list(db.execute(stmt).scalars().all())
    messages.reverse()
    return messages


def create_chat_message(
    db: Session,
    *,
    session: ChatSession,
    role: str,
    content: str,
    context_text: str | None = None,
    sources_json: str | None = None,
    chunk_count: int = 0,
    used_context: bool = False,
) -> ChatMessage:
    message = ChatMessage(
        session_id=session.id,
        role=role,
        content=content,
        context_text=context_text,
        sources_json=sources_json,
        chunk_count=chunk_count,
        used_context=used_context,
    )
    session.updated_at = datetime.now(UTC)
    db.add(message)
    db.add(session)
    db.commit()
    db.refresh(message)
    return message
