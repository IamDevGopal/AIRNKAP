from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.document_model import Document
from app.models.user_model import User
from app.repositories.document_repository import (
    create_document,
    get_document_by_owner_and_id,
    get_document_by_project_and_title,
    list_documents_by_owner,
    update_document,
)
from app.repositories.project_repository import get_project_by_owner_and_id
from app.schemas.document_schema import DocumentCreateRequest, DocumentUpdateRequest


def create_user_document(
    db: Session, current_user: User, payload: DocumentCreateRequest
) -> Document:
    project = get_project_by_owner_and_id(db, current_user.id, payload.project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    existing = get_document_by_project_and_title(db, project.id, payload.title.strip())
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Document with this title already exists in project",
        )

    return create_document(
        db=db,
        owner_id=current_user.id,
        workspace_id=project.workspace_id,
        project_id=project.id,
        title=payload.title.strip(),
        source_type=payload.source_type,
        source_uri=payload.source_uri,
        content_text=payload.content_text,
    )


def list_user_documents(
    db: Session,
    current_user: User,
    project_id: int | None = None,
) -> list[Document]:
    if project_id is not None:
        project = get_project_by_owner_and_id(db, current_user.id, project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found",
            )
    return list_documents_by_owner(db, current_user.id, project_id)


def get_user_document(db: Session, current_user: User, document_id: int) -> Document:
    document = get_document_by_owner_and_id(db, current_user.id, document_id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )
    return document


def update_user_document(
    db: Session,
    current_user: User,
    document_id: int,
    payload: DocumentUpdateRequest,
) -> Document:
    document = get_user_document(db, current_user, document_id)

    if payload.title is not None:
        new_title = payload.title.strip()
        existing = get_document_by_project_and_title(db, document.project_id, new_title)
        if existing and existing.id != document.id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Document with this title already exists in project",
            )
        document.title = new_title

    if payload.source_type is not None:
        document.source_type = payload.source_type

    if payload.source_uri is not None:
        document.source_uri = payload.source_uri

    if payload.content_text is not None:
        document.content_text = payload.content_text

    if payload.status is not None:
        document.status = payload.status

    return update_document(db, document)


def delete_user_document(db: Session, current_user: User, document_id: int) -> None:
    document = get_user_document(db, current_user, document_id)
    document.status = "deleted"
    update_document(db, document)
