from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models.user_model import User
from app.schemas.knowledge_schema import (
    DocumentKnowledgeQueryRequest,
    KnowledgeQueryRequest,
    KnowledgeQueryResponse,
    ProjectKnowledgeQueryRequest,
)
from app.services.knowledge_service import run_knowledge_query

router = APIRouter(prefix="/knowledge", tags=["knowledge"])


@router.post("/query", response_model=KnowledgeQueryResponse)
def query_knowledge(
    payload: KnowledgeQueryRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> KnowledgeQueryResponse:
    return run_knowledge_query(
        db=db,
        current_user=current_user,
        query_text=payload.query_text,
        scope_type=payload.scope_type,
        scope_id=payload.scope_id,
        top_k=payload.top_k,
        max_context_chunks=payload.max_context_chunks,
    )


@router.post("/query/document", response_model=KnowledgeQueryResponse)
def query_document_knowledge(
    payload: DocumentKnowledgeQueryRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> KnowledgeQueryResponse:
    return run_knowledge_query(
        db=db,
        current_user=current_user,
        query_text=payload.query_text,
        scope_type="document",
        scope_id=payload.document_id,
        top_k=payload.top_k,
        max_context_chunks=payload.max_context_chunks,
    )


@router.post("/query/project", response_model=KnowledgeQueryResponse)
def query_project_knowledge(
    payload: ProjectKnowledgeQueryRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> KnowledgeQueryResponse:
    return run_knowledge_query(
        db=db,
        current_user=current_user,
        query_text=payload.query_text,
        scope_type="project",
        scope_id=payload.project_id,
        top_k=payload.top_k,
        max_context_chunks=payload.max_context_chunks,
    )
