from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.report_model import Report


def create_report(
    db: Session,
    *,
    owner_id: int,
    workspace_id: int,
    project_id: int,
    title: str,
    report_type: str,
    instruction: str | None,
    source_task_ids_json: str,
    content_text: str,
) -> Report:
    report = Report(
        owner_id=owner_id,
        workspace_id=workspace_id,
        project_id=project_id,
        title=title,
        report_type=report_type,
        instruction=instruction,
        source_task_ids_json=source_task_ids_json,
        content_text=content_text,
        status="generated",
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return report


def list_reports_by_owner(
    db: Session,
    owner_id: int,
    *,
    limit: int = 50,
    offset: int = 0,
) -> list[Report]:
    stmt = (
        select(Report)
        .where(Report.owner_id == owner_id)
        .order_by(Report.created_at.desc(), Report.id.desc())
        .limit(limit)
        .offset(offset)
    )
    return list(db.execute(stmt).scalars().all())


def get_report_by_owner_and_id(
    db: Session,
    owner_id: int,
    report_id: int,
) -> Report | None:
    stmt = select(Report).where(
        Report.owner_id == owner_id,
        Report.id == report_id,
    )
    return db.execute(stmt).scalar_one_or_none()


def delete_report(db: Session, report: Report) -> None:
    db.delete(report)
    db.commit()
