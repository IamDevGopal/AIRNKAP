from fastapi import APIRouter, Depends, File, Form, Query, UploadFile, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models.user_model import User
from app.schemas.document_schema import (
    DocumentDeleteResponse,
    DocumentResponse,
    DocumentUpdateRequest,
)
from app.services.document_service import (
    create_user_document_from_upload,
    delete_user_document,
    get_user_document,
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
