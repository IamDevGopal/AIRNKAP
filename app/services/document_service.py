from pathlib import Path
import shutil
from uuid import uuid4

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.models.document_chunk_model import DocumentChunk
from app.models.document_model import Document
from app.models.user_model import User
from app.repositories.document_repository import (
    create_document,
    get_document_by_owner_and_id,
    get_document_by_project_and_title,
    list_document_chunks_by_document_id,
    list_documents_by_owner,
    update_document,
    update_document_ingestion_fields,
)
from app.repositories.project_repository import get_project_by_owner_and_id
from app.schemas.document_schema import DocumentUpdateRequest
from app.tasks.document_dispatch import enqueue_document_ingestion_job


def _safe_file_name(filename: str) -> str:
    return Path(filename).name.replace("\\", "_").replace("/", "_")


def _persist_uploaded_file(
    upload: UploadFile,
    owner_id: int,
    workspace_id: int,
    project_id: int,
) -> tuple[str, str, int | None, str | None]:
    safe_original = _safe_file_name(upload.filename or "document.bin")
    unique_name = f"{uuid4().hex}_{safe_original}"
    base_dir = Path("data") / "raw_documents" / str(owner_id) / str(workspace_id) / str(project_id)
    base_dir.mkdir(parents=True, exist_ok=True)
    file_path = base_dir / unique_name

    with file_path.open("wb") as target:
        upload.file.seek(0)
        shutil.copyfileobj(upload.file, target)

    size = file_path.stat().st_size if file_path.exists() else None
    return safe_original, file_path.as_posix(), size, upload.content_type


def create_user_document_from_upload(
    db: Session,
    current_user: User,
    project_id: int,
    upload: UploadFile,
    title: str | None = None,
    source_uri: str | None = None,
) -> Document:
    project = get_project_by_owner_and_id(db, current_user.id, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    if not upload.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file must have a filename",
        )

    resolved_title = (title or Path(upload.filename).stem).strip()
    if not resolved_title:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Document title cannot be empty",
        )

    existing = get_document_by_project_and_title(db, project.id, resolved_title)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Document with this title already exists in project",
        )

    file_name, file_path, file_size_bytes, mime_type = _persist_uploaded_file(
        upload=upload,
        owner_id=current_user.id,
        workspace_id=project.workspace_id,
        project_id=project.id,
    )

    document = create_document(
        db=db,
        owner_id=current_user.id,
        workspace_id=project.workspace_id,
        project_id=project.id,
        title=resolved_title,
        file_name=file_name,
        file_path=file_path,
        file_size_bytes=file_size_bytes,
        mime_type=mime_type,
        source_type="file",
        source_uri=source_uri,
        content_text=None,
    )

    enqueue_document_ingestion_job(document.id)
    return document


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


def get_user_document_ingestion_status(
    db: Session, current_user: User, document_id: int
) -> Document:
    return get_user_document(db, current_user, document_id)


def list_user_document_chunks(
    db: Session,
    current_user: User,
    document_id: int,
    limit: int = 200,
    offset: int = 0,
) -> list[DocumentChunk]:
    document = get_user_document(db, current_user, document_id)
    return list_document_chunks_by_document_id(
        db=db,
        document_id=document.id,
        limit=limit,
        offset=offset,
    )


def reindex_user_document(db: Session, current_user: User, document_id: int) -> Document:
    document = get_user_document(db, current_user, document_id)
    if document.status != "active":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Only active documents can be reindexed",
        )
    if not document.file_path:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Document does not have a file path to reindex",
        )

    queued_document = update_document_ingestion_fields(
        db,
        document,
        ingestion_status="queued",
        ingestion_error=None,
        ingestion_started_at=None,
        ingestion_completed_at=None,
    )
    enqueue_document_ingestion_job(queued_document.id)
    return queued_document
