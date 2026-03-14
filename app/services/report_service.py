import json
from typing import cast

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.ai.llm.wrappers.chat import generate_contextual_response
from app.models.report_model import Report
from app.models.research_task_model import ResearchTask
from app.models.user_model import User
from app.repositories.project_repository import get_project_by_owner_and_id
from app.repositories.report_repository import (
    create_report,
    delete_report,
    get_report_by_owner_and_id,
    list_reports_by_owner,
)
from app.repositories.research_repository import get_research_task_by_owner_and_id
from app.schemas.report_schema import (
    ReportDeleteResponse,
    ReportGenerateRequest,
    ReportResponse,
    ReportStatus,
    ReportType,
)


def generate_user_report(
    *,
    db: Session,
    current_user: User,
    payload: ReportGenerateRequest,
) -> ReportResponse:
    project = get_project_by_owner_and_id(db, current_user.id, payload.project_id)
    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    tasks = []
    for task_id in payload.source_task_ids:
        task = get_research_task_by_owner_and_id(db, current_user.id, task_id)
        if task is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Research task {task_id} not found",
            )
        if task.project_id != project.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Research task {task_id} does not belong to the selected project",
            )
        if task.status != "completed":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Research task {task_id} must be completed before report generation",
            )
        tasks.append(task)

    compiled_context = _build_report_context(tasks)
    content_text = generate_contextual_response(
        system_instruction=_build_report_system_instruction(payload.report_type),
        user_instruction=_build_report_user_instruction(
            title=payload.title,
            report_type=payload.report_type,
            instruction=payload.instruction,
        ),
        context_text=compiled_context,
        response_instruction=_build_report_response_instruction(payload.report_type),
    )

    report = create_report(
        db,
        owner_id=current_user.id,
        workspace_id=project.workspace_id,
        project_id=project.id,
        title=payload.title,
        report_type=payload.report_type,
        instruction=payload.instruction,
        source_task_ids_json=json.dumps(payload.source_task_ids),
        content_text=content_text,
    )
    return _serialize_report(report)


def list_user_reports(
    *,
    db: Session,
    current_user: User,
) -> list[ReportResponse]:
    reports = list_reports_by_owner(db, current_user.id)
    return [_serialize_report(report) for report in reports]


def get_user_report(
    *,
    db: Session,
    current_user: User,
    report_id: int,
) -> ReportResponse:
    report = _get_owned_report(db, current_user.id, report_id)
    return _serialize_report(report)


def delete_user_report(
    *,
    db: Session,
    current_user: User,
    report_id: int,
) -> ReportDeleteResponse:
    report = _get_owned_report(db, current_user.id, report_id)
    delete_report(db, report)
    return ReportDeleteResponse(message="Report deleted successfully")


def _get_owned_report(db: Session, owner_id: int, report_id: int) -> Report:
    report = get_report_by_owner_and_id(db, owner_id, report_id)
    if report is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found",
        )
    return report


def _serialize_report(report: Report) -> ReportResponse:
    source_task_ids = cast(list[int], json.loads(report.source_task_ids_json))
    return ReportResponse(
        id=report.id,
        title=report.title,
        report_type=cast(ReportType, report.report_type),
        project_id=report.project_id,
        workspace_id=report.workspace_id,
        status=cast(ReportStatus, report.status),
        instruction=report.instruction,
        source_task_ids=source_task_ids,
        content_text=report.content_text,
        created_at=report.created_at,
        updated_at=report.updated_at,
    )


def _build_report_context(tasks: list[ResearchTask]) -> str:
    sections: list[str] = []
    for index, task in enumerate(tasks, start=1):
        sections.append(
            "\n".join(
                [
                    f"Task {index}: {task.title}",
                    f"Task Type: {task.task_type}",
                    f"Instruction: {task.instruction}",
                    "Task Output:",
                    (task.result_text or "").strip(),
                ]
            ).strip()
        )
    return "\n\n".join(section for section in sections if section)


def _build_report_system_instruction(report_type: ReportType) -> str:
    prompts: dict[ReportType, str] = {
        "executive_summary": (
            "You create concise executive summaries from the provided grounded research outputs."
        ),
        "research_brief": (
            "You create structured research briefs using only the provided grounded task outputs."
        ),
        "risk_report": (
            "You create risk-focused reports using only the provided grounded task outputs."
        ),
        "custom": ("You create a report using only the provided grounded task outputs."),
    }
    return prompts[report_type]


def _build_report_response_instruction(report_type: ReportType) -> str:
    outputs: dict[ReportType, str] = {
        "executive_summary": (
            "Return a concise executive summary with clear sections and key takeaways."
        ),
        "research_brief": (
            "Return a structured research brief with headings, evidence synthesis, and conclusions."
        ),
        "risk_report": (
            "Return a risk report with organized sections, risk groupings, and concise recommendations."
        ),
        "custom": "Return a clear, well-structured report.",
    }
    return outputs[report_type]


def _build_report_user_instruction(
    *,
    title: str,
    report_type: ReportType,
    instruction: str | None,
) -> str:
    if instruction:
        return (
            f"Report Title:\n{title}\n\n"
            f"Report Type:\n{report_type}\n\n"
            f"Additional Instruction:\n{instruction}"
        )
    return f"Report Title:\n{title}\n\nReport Type:\n{report_type}"
