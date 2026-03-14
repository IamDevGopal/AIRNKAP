import json
from typing import cast

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.ai.llm.wrappers.chat import generate_grounded_answer
from app.ai.rag.retrieval import (
    RetrievalRequest,
    RetrievalScope,
    run_retrieval_pipeline,
)
from app.ai.rag.retrieval.context_builder import ContextSource
from app.config import get_settings
from app.models.chat_message_model import ChatMessage
from app.models.chat_session_model import ChatSession
from app.models.user_model import User
from app.repositories.chat_repository import (
    create_chat_message,
    create_chat_session,
    delete_chat_session,
    get_chat_session_by_owner_and_id,
    list_chat_messages_by_session_id,
    list_chat_sessions_by_owner,
    list_recent_chat_messages,
)
from app.repositories.document_repository import get_document_by_owner_and_id
from app.repositories.project_repository import get_project_by_owner_and_id
from app.schemas.knowledge_schema import KnowledgeScopeType
from app.schemas.research_schema import (
    ChatMessageRequest,
    ChatMessageResponse,
    ChatMessageSourceResponse,
    ChatRole,
    ChatSessionDeleteResponse,
    ChatSessionDetailResponse,
    ChatSessionSummaryResponse,
    ChatTurnResponse,
)

settings = get_settings()


def send_chat_message(
    *,
    db: Session,
    current_user: User,
    payload: ChatMessageRequest,
) -> ChatTurnResponse:
    session, created_new_session = _resolve_chat_session(
        db=db,
        current_user=current_user,
        payload=payload,
    )
    history = _build_chat_history(
        list_recent_chat_messages(
            db,
            session.id,
            settings.chat_history_messages_limit,
        )
    )
    user_message = create_chat_message(
        db,
        session=session,
        role="user",
        content=payload.message,
    )

    retrieval_response = run_retrieval_pipeline(
        RetrievalRequest(
            query_text=payload.message,
            scope=RetrievalScope(
                scope_type=cast(KnowledgeScopeType, session.scope_type),
                scope_id=session.scope_id,
            ),
            top_k=payload.top_k,
            max_context_chunks=payload.max_context_chunks,
        )
    )
    context_text = retrieval_response.context.context_text.strip()
    used_context = bool(context_text)
    if used_context:
        assistant_content = generate_grounded_answer(
            query_text=payload.message,
            context_text=context_text,
            chat_history=history,
        )
    else:
        assistant_content = "No relevant context was found in the selected knowledge scope."

    assistant_message = create_chat_message(
        db,
        session=session,
        role="assistant",
        content=assistant_content,
        context_text=context_text,
        sources_json=json.dumps(
            [_serialize_source(source) for source in retrieval_response.context.sources]
        ),
        chunk_count=retrieval_response.context.chunk_count,
        used_context=used_context,
    )

    refreshed_session = get_chat_session_by_owner_and_id(db, current_user.id, session.id)
    if refreshed_session is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Chat session could not be reloaded",
        )

    return ChatTurnResponse(
        created_new_session=created_new_session,
        session=_serialize_session(refreshed_session),
        user_message=_serialize_message(user_message),
        assistant_message=_serialize_message(assistant_message),
    )


def list_user_chat_sessions(
    *,
    db: Session,
    current_user: User,
) -> list[ChatSessionSummaryResponse]:
    sessions = list_chat_sessions_by_owner(db, current_user.id)
    return [_serialize_session(session) for session in sessions]


def get_chat_session_detail(
    *,
    db: Session,
    current_user: User,
    session_id: int,
) -> ChatSessionDetailResponse:
    session = _get_owned_session(db, current_user.id, session_id)
    messages = list_chat_messages_by_session_id(db, session.id)
    return ChatSessionDetailResponse(
        session=_serialize_session(session),
        messages=[_serialize_message(message) for message in messages],
    )


def delete_user_chat_session(
    *,
    db: Session,
    current_user: User,
    session_id: int,
) -> ChatSessionDeleteResponse:
    session = _get_owned_session(db, current_user.id, session_id)
    delete_chat_session(db, session)
    return ChatSessionDeleteResponse(message="Chat session deleted successfully")


def _resolve_chat_session(
    *,
    db: Session,
    current_user: User,
    payload: ChatMessageRequest,
) -> tuple[ChatSession, bool]:
    if payload.session_id is not None:
        session = _get_owned_session(db, current_user.id, payload.session_id)
        if payload.scope_type is not None and payload.scope_type != session.scope_type:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="scope_type does not match the existing session",
            )
        if payload.scope_id is not None and payload.scope_id != session.scope_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="scope_id does not match the existing session",
            )
        return session, False

    if payload.scope_type is None or payload.scope_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="scope_type and scope_id are required for a new chat session",
        )

    workspace_id, project_id, document_id = _resolve_scope_ids(
        db=db,
        current_user=current_user,
        scope_type=payload.scope_type,
        scope_id=payload.scope_id,
    )
    session = create_chat_session(
        db,
        owner_id=current_user.id,
        workspace_id=workspace_id,
        project_id=project_id,
        document_id=document_id,
        scope_type=payload.scope_type,
        scope_id=payload.scope_id,
        title=_build_session_title(payload.message),
    )
    return session, True


def _resolve_scope_ids(
    *,
    db: Session,
    current_user: User,
    scope_type: KnowledgeScopeType,
    scope_id: int,
) -> tuple[int, int, int | None]:
    if scope_type == "document":
        document = get_document_by_owner_and_id(db, current_user.id, scope_id)
        if document is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found",
            )
        return document.workspace_id, document.project_id, document.id

    project = get_project_by_owner_and_id(db, current_user.id, scope_id)
    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
    return project.workspace_id, project.id, None


def _get_owned_session(db: Session, owner_id: int, session_id: int) -> ChatSession:
    session = get_chat_session_by_owner_and_id(db, owner_id, session_id)
    if session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found",
        )
    return session


def _build_session_title(message: str) -> str:
    normalized = " ".join(message.split())
    if len(normalized) <= 80:
        return normalized
    return f"{normalized[:77].rstrip()}..."


def _build_chat_history(messages: list[ChatMessage]) -> list[tuple[str, str]]:
    history: list[tuple[str, str]] = []
    for message in messages:
        history.append((message.role, message.content))
    return history


def _serialize_session(session: ChatSession) -> ChatSessionSummaryResponse:
    return ChatSessionSummaryResponse(
        id=session.id,
        title=session.title,
        scope_type=cast(KnowledgeScopeType, session.scope_type),
        scope_id=session.scope_id,
        workspace_id=session.workspace_id,
        project_id=session.project_id,
        document_id=session.document_id,
        created_at=session.created_at,
        updated_at=session.updated_at,
    )


def _serialize_message(message: ChatMessage) -> ChatMessageResponse:
    return ChatMessageResponse(
        id=message.id,
        role=cast(ChatRole, message.role),
        content=message.content,
        context_text=message.context_text,
        chunk_count=message.chunk_count,
        used_context=message.used_context,
        sources=_deserialize_sources(message.sources_json),
        created_at=message.created_at,
    )


def _deserialize_sources(sources_json: str | None) -> list[ChatMessageSourceResponse]:
    if not sources_json:
        return []
    raw_sources = json.loads(sources_json)
    return [ChatMessageSourceResponse.model_validate(item) for item in raw_sources]


def _serialize_source(source: ContextSource) -> dict[str, int | float | None]:
    return {
        "document_id": source.document_id,
        "project_id": source.project_id,
        "workspace_id": source.workspace_id,
        "chunk_index": source.chunk_index,
        "score": source.score,
    }
