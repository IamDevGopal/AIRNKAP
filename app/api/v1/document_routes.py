from typing import cast

from fastapi import APIRouter, Depends, File, Form, Query, UploadFile, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models.user_model import User
from app.schemas.document_ingestion_schema import (
    DocumentChunkResponse,
    DocumentIngestionStatus,
    DocumentIngestionStatusResponse,
)
from app.schemas.document_schema import (
    DocumentDeleteResponse,
    DocumentResponse,
    DocumentUpdateRequest,
)
from app.services.document_service import (
    create_user_document_from_upload,
    delete_user_document,
    get_user_document,
    get_user_document_ingestion_status,
    list_user_document_chunks,
    list_user_documents,
    update_user_document,
)

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
def upload_document(
    project_id: int = Form(...),
    title: str | None = Form(default=None),
    source_uri: str | None = Form(default=None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DocumentResponse:
    document = create_user_document_from_upload(
        db=db,
        current_user=current_user,
        project_id=project_id,
        upload=file,
        title=title,
        source_uri=source_uri,
    )
    return DocumentResponse.model_validate(document)


@router.get("", response_model=list[DocumentResponse])
def list_documents(
    project_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[DocumentResponse]:
    documents = list_user_documents(db, current_user, project_id)
    return [DocumentResponse.model_validate(document) for document in documents]


@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DocumentResponse:
    document = get_user_document(db, current_user, document_id)
    return DocumentResponse.model_validate(document)


@router.patch("/{document_id}", response_model=DocumentResponse)
def update_document(
    document_id: int,
    payload: DocumentUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DocumentResponse:
    document = update_user_document(db, current_user, document_id, payload)
    return DocumentResponse.model_validate(document)


@router.delete("/{document_id}", response_model=DocumentDeleteResponse)
def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DocumentDeleteResponse:
    delete_user_document(db, current_user, document_id)
    return DocumentDeleteResponse(message="Document deleted successfully")


@router.get("/{document_id}/status", response_model=DocumentIngestionStatusResponse)
def get_document_status(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DocumentIngestionStatusResponse:
    document = get_user_document_ingestion_status(db, current_user, document_id)
    return DocumentIngestionStatusResponse(
        document_id=document.id,
        ingestion_status=cast(DocumentIngestionStatus, document.ingestion_status),
        ingestion_error=document.ingestion_error,
        ingestion_started_at=document.ingestion_started_at,
        ingestion_completed_at=document.ingestion_completed_at,
        chunk_count=document.chunk_count,
        embedding_model=document.embedding_model,
        embedding_version=document.embedding_version,
        updated_at=document.updated_at,
    )


@router.get("/{document_id}/chunks", response_model=list[DocumentChunkResponse])
def list_document_chunks(
    document_id: int,
    limit: int = Query(default=200, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[DocumentChunkResponse]:
    chunks = list_user_document_chunks(
        db=db,
        current_user=current_user,
        document_id=document_id,
        limit=limit,
        offset=offset,
    )
    return [DocumentChunkResponse.model_validate(chunk) for chunk in chunks]
