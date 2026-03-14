"""create_automation_workflows_tables

Revision ID: b2a1c4d9e8f0
Revises: f7b8c2d1e4a6
Create Date: 2026-03-14 18:30:00.000000

"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "b2a1c4d9e8f0"
down_revision: str | Sequence[str] | None = "f7b8c2d1e4a6"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "automation_workflows",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("owner_id", sa.Integer(), nullable=False),
        sa.Column("workspace_id", sa.Integer(), nullable=False),
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("document_id", sa.Integer(), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("workflow_type", sa.String(length=50), nullable=False),
        sa.Column("trigger_type", sa.String(length=30), server_default="manual", nullable=False),
        sa.Column("scope_type", sa.String(length=30), nullable=False),
        sa.Column("scope_id", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=30), server_default="active", nullable=False),
        sa.Column("config_json", sa.Text(), nullable=False),
        sa.Column("run_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("last_run_status", sa.String(length=30), nullable=True),
        sa.Column("last_run_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["workspace_id"], ["workspaces.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_automation_workflows_document_id"),
        "automation_workflows",
        ["document_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_automation_workflows_id"), "automation_workflows", ["id"], unique=False
    )
    op.create_index(
        op.f("ix_automation_workflows_owner_id"),
        "automation_workflows",
        ["owner_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_automation_workflows_project_id"),
        "automation_workflows",
        ["project_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_automation_workflows_scope_id"),
        "automation_workflows",
        ["scope_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_automation_workflows_workspace_id"),
        "automation_workflows",
        ["workspace_id"],
        unique=False,
    )

    op.create_table(
        "automation_workflow_runs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("workflow_id", sa.Integer(), nullable=False),
        sa.Column("owner_id", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=30), server_default="running", nullable=False),
        sa.Column("result_entity_type", sa.String(length=50), nullable=True),
        sa.Column("result_entity_id", sa.Integer(), nullable=True),
        sa.Column("result_text", sa.Text(), nullable=True),
        sa.Column("error_message", sa.String(length=3000), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["workflow_id"],
            ["automation_workflows.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_automation_workflow_runs_id"),
        "automation_workflow_runs",
        ["id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_automation_workflow_runs_owner_id"),
        "automation_workflow_runs",
        ["owner_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_automation_workflow_runs_workflow_id"),
        "automation_workflow_runs",
        ["workflow_id"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(
        op.f("ix_automation_workflow_runs_workflow_id"), table_name="automation_workflow_runs"
    )
    op.drop_index(
        op.f("ix_automation_workflow_runs_owner_id"), table_name="automation_workflow_runs"
    )
    op.drop_index(op.f("ix_automation_workflow_runs_id"), table_name="automation_workflow_runs")
    op.drop_table("automation_workflow_runs")

    op.drop_index(op.f("ix_automation_workflows_workspace_id"), table_name="automation_workflows")
    op.drop_index(op.f("ix_automation_workflows_scope_id"), table_name="automation_workflows")
    op.drop_index(op.f("ix_automation_workflows_project_id"), table_name="automation_workflows")
    op.drop_index(op.f("ix_automation_workflows_owner_id"), table_name="automation_workflows")
    op.drop_index(op.f("ix_automation_workflows_id"), table_name="automation_workflows")
    op.drop_index(op.f("ix_automation_workflows_document_id"), table_name="automation_workflows")
    op.drop_table("automation_workflows")
