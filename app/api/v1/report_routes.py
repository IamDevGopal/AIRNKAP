from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models.user_model import User
from app.schemas.report_schema import (
    ReportDeleteResponse,
    ReportGenerateRequest,
    ReportResponse,
)
from app.services.report_service import (
    delete_user_report,
    generate_user_report,
    get_user_report,
    list_user_reports,
)

router = APIRouter(prefix="/reports", tags=["reports"])


@router.post("/generate", response_model=ReportResponse)
def generate_report(
    payload: ReportGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ReportResponse:
    return generate_user_report(
        db=db,
        current_user=current_user,
        payload=payload,
    )


@router.get("", response_model=list[ReportResponse])
def list_reports(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[ReportResponse]:
    return list_user_reports(
        db=db,
        current_user=current_user,
    )


@router.get("/{report_id}", response_model=ReportResponse)
def get_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ReportResponse:
    return get_user_report(
        db=db,
        current_user=current_user,
        report_id=report_id,
    )


@router.delete("/{report_id}", response_model=ReportDeleteResponse)
def remove_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ReportDeleteResponse:
    return delete_user_report(
        db=db,
        current_user=current_user,
        report_id=report_id,
    )
