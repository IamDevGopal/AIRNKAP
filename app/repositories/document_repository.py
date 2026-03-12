from sqlalchemy import select
from sqlalchemy.orm import Session

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
    source_uri: str | None = None,
    content_text: str | None = None,
) -> Document:
    document = Document(
        owner_id=owner_id,
        workspace_id=workspace_id,
        project_id=project_id,
        title=title,
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
