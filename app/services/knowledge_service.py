from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.ai.llm.wrappers.chat import generate_grounded_answer
from app.ai.rag.retrieval import (
    RetrievalRequest,
    RetrievalScope,
    run_retrieval_pipeline,
)
from app.models.user_model import User
from app.repositories.document_repository import get_document_by_owner_and_id
from app.repositories.project_repository import get_project_by_owner_and_id
from app.schemas.knowledge_schema import (
    KnowledgeQueryResponse,
    KnowledgeQuerySourceResponse,
    KnowledgeScopeType,
)


def run_knowledge_query(
    *,
    db: Session,
    current_user: User,
    query_text: str,
    scope_type: KnowledgeScopeType,
    scope_id: int,
    top_k: int = 5,
    max_context_chunks: int = 5,
) -> KnowledgeQueryResponse:
    _validate_query_scope(
        db=db,
        current_user=current_user,
        scope_type=scope_type,
        scope_id=scope_id,
    )

    retrieval_response = run_retrieval_pipeline(
        RetrievalRequest(
            query_text=query_text,
            scope=RetrievalScope(scope_type=scope_type, scope_id=scope_id),
            top_k=top_k,
            max_context_chunks=max_context_chunks,
        )
    )

    context_text = retrieval_response.context.context_text.strip()
    used_context = bool(context_text)

    if used_context:
        answer = generate_grounded_answer(
            query_text=query_text,
            context_text=context_text,
        )
    else:
        answer = "No relevant context was found in the selected knowledge scope."

    return KnowledgeQueryResponse(
        query_text=query_text,
        scope_type=scope_type,
        scope_id=scope_id,
        answer=answer,
        context_text=context_text,
        chunk_count=retrieval_response.context.chunk_count,
        sources=[
            KnowledgeQuerySourceResponse(
                document_id=source.document_id,
                project_id=source.project_id,
                workspace_id=source.workspace_id,
                chunk_index=source.chunk_index,
                score=source.score,
            )
            for source in retrieval_response.context.sources
        ],
        used_context=used_context,
    )


def _validate_query_scope(
    *,
    db: Session,
    current_user: User,
    scope_type: KnowledgeScopeType,
    scope_id: int,
) -> None:
    if scope_type == "document":
        document = get_document_by_owner_and_id(db, current_user.id, scope_id)
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found",
            )
        return

    if scope_type == "project":
        project = get_project_by_owner_and_id(db, current_user.id, scope_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found",
            )
        return

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Unsupported query scope",
    )
