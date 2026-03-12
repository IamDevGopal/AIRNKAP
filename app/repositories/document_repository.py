from datetime import datetime

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models.document_chunk_model import DocumentChunk
from app.models.document_model import Document


def list_documents_by_owner(
    db: Session,
    owner_id: int,
    project_id: int | None = None,
) -> list[Document]:
    stmt = select(Document).where(Document.owner_id == owner_id)
    if project_id is not None:
        stmt = stmt.where(Document.project_id == project_id)
    stmt = stmt.order_by(Document.id.desc())
    return list(db.execute(stmt).scalars().all())


def get_document_by_owner_and_id(db: Session, owner_id: int, document_id: int) -> Document | None:
    stmt = select(Document).where(
        Document.owner_id == owner_id,
        Document.id == document_id,
    )
    return db.execute(stmt).scalar_one_or_none()


def get_document_by_id(db: Session, document_id: int) -> Document | None:
    stmt = select(Document).where(Document.id == document_id)
    return db.execute(stmt).scalar_one_or_none()


def get_document_by_project_and_title(
    db: Session,
    project_id: int,
    title: str,
) -> Document | None:
    stmt = select(Document).where(
        Document.project_id == project_id,
        Document.title == title,
    )
    return db.execute(stmt).scalar_one_or_none()


def create_document(
    db: Session,
    owner_id: int,
    workspace_id: int,
    project_id: int,
    title: str,
    source_type: str,
    file_name: str,
    file_path: str,
    file_size_bytes: int | None = None,
    mime_type: str | None = None,
    source_uri: str | None = None,
    content_text: str | None = None,
) -> Document:
    document = Document(
        owner_id=owner_id,
        workspace_id=workspace_id,
        project_id=project_id,
        title=title,
        file_name=file_name,
        file_path=file_path,
        file_size_bytes=file_size_bytes,
        mime_type=mime_type,
        source_type=source_type,
        source_uri=source_uri,
        content_text=content_text,
        status="active",
    )
    db.add(document)
    db.commit()
    db.refresh(document)
    return document


def update_document(db: Session, document: Document) -> Document:
    db.add(document)
    db.commit()
    db.refresh(document)
    return document


def update_document_ingestion_fields(
    db: Session,
    document: Document,
    *,
    ingestion_status: str,
    ingestion_error: str | None = None,
    ingestion_started_at: datetime | None = None,
    ingestion_completed_at: datetime | None = None,
    chunk_count: int | None = None,
    embedding_model: str | None = None,
    embedding_version: str | None = None,
    content_hash: str | None = None,
) -> Document:
    document.ingestion_status = ingestion_status
    document.ingestion_error = ingestion_error
    document.ingestion_started_at = ingestion_started_at
    document.ingestion_completed_at = ingestion_completed_at

    if chunk_count is not None:
        document.chunk_count = chunk_count
    if embedding_model is not None:
        document.embedding_model = embedding_model
    if embedding_version is not None:
        document.embedding_version = embedding_version
    if content_hash is not None:
        document.content_hash = content_hash

    return update_document(db, document)


def list_document_chunks_by_document_id(
    db: Session,
    document_id: int,
    limit: int = 200,
    offset: int = 0,
) -> list[DocumentChunk]:
    stmt = (
        select(DocumentChunk)
        .where(DocumentChunk.document_id == document_id)
        .order_by(DocumentChunk.chunk_index.asc())
        .limit(limit)
        .offset(offset)
    )
    return list(db.execute(stmt).scalars().all())


def replace_document_chunks(
    db: Session,
    document_id: int,
    chunks: list[tuple[int, str, int | None]],
) -> list[DocumentChunk]:
    db.execute(delete(DocumentChunk).where(DocumentChunk.document_id == document_id))

    created_chunks: list[DocumentChunk] = []
    for chunk_index, chunk_text, token_count in chunks:
        chunk = DocumentChunk(
            document_id=document_id,
            chunk_index=chunk_index,
            chunk_text=chunk_text,
            token_count=token_count,
        )
        db.add(chunk)
        created_chunks.append(chunk)

    db.commit()
    for chunk in created_chunks:
        db.refresh(chunk)
    return created_chunks
