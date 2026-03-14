from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.automation_workflow_model import AutomationWorkflow
from app.models.automation_workflow_run_model import AutomationWorkflowRun


def create_automation_workflow(
    db: Session,
    *,
    owner_id: int,
    workspace_id: int,
    project_id: int,
    document_id: int | None,
    name: str,
    description: str | None,
    workflow_type: str,
    trigger_type: str,
    scope_type: str,
    scope_id: int,
    config_json: str,
) -> AutomationWorkflow:
    workflow = AutomationWorkflow(
        owner_id=owner_id,
        workspace_id=workspace_id,
        project_id=project_id,
        document_id=document_id,
        name=name,
        description=description,
        workflow_type=workflow_type,
        trigger_type=trigger_type,
        scope_type=scope_type,
        scope_id=scope_id,
        status="active",
        config_json=config_json,
    )
    db.add(workflow)
    db.commit()
    db.refresh(workflow)
    return workflow


def list_automation_workflows_by_owner(
    db: Session,
    owner_id: int,
    *,
    limit: int = 50,
    offset: int = 0,
) -> list[AutomationWorkflow]:
    stmt = (
        select(AutomationWorkflow)
        .where(AutomationWorkflow.owner_id == owner_id)
        .order_by(AutomationWorkflow.created_at.desc(), AutomationWorkflow.id.desc())
        .limit(limit)
        .offset(offset)
    )
    return list(db.execute(stmt).scalars().all())


def get_automation_workflow_by_owner_and_id(
    db: Session,
    owner_id: int,
    workflow_id: int,
) -> AutomationWorkflow | None:
    stmt = select(AutomationWorkflow).where(
        AutomationWorkflow.owner_id == owner_id,
        AutomationWorkflow.id == workflow_id,
    )
    return db.execute(stmt).scalar_one_or_none()


def update_automation_workflow(db: Session, workflow: AutomationWorkflow) -> AutomationWorkflow:
    db.add(workflow)
    db.commit()
    db.refresh(workflow)
    return workflow


def create_automation_workflow_run(
    db: Session,
    *,
    workflow_id: int,
    owner_id: int,
    started_at: datetime,
) -> AutomationWorkflowRun:
    run = AutomationWorkflowRun(
        workflow_id=workflow_id,
        owner_id=owner_id,
        status="running",
        started_at=started_at,
    )
    db.add(run)
    db.commit()
    db.refresh(run)
    return run


def update_automation_workflow_run(
    db: Session,
    run: AutomationWorkflowRun,
) -> AutomationWorkflowRun:
    db.add(run)
    db.commit()
    db.refresh(run)
    return run
