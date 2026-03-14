"""create_research_tasks_table

Revision ID: c4de29a6f9b1
Revises: ab3c9d4e7f21
Create Date: 2026-03-14 13:05:00.000000

"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "c4de29a6f9b1"
down_revision: str | Sequence[str] | None = "ab3c9d4e7f21"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "research_tasks",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("owner_id", sa.Integer(), nullable=False),
        sa.Column("workspace_id", sa.Integer(), nullable=False),
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("document_id", sa.Integer(), nullable=True),
        sa.Column("task_type", sa.String(length=50), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("instruction", sa.Text(), nullable=False),
        sa.Column("scope_type", sa.String(length=30), nullable=False),
        sa.Column("scope_id", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=30), server_default="pending", nullable=False),
        sa.Column("result_text", sa.Text(), nullable=True),
        sa.Column("result_sources_json", sa.Text(), nullable=True),
        sa.Column("result_chunk_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("error_message", sa.String(length=3000), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("cancelled_at", sa.DateTime(timezone=True), nullable=True),
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
        op.f("ix_research_tasks_document_id"), "research_tasks", ["document_id"], unique=False
    )
    op.create_index(op.f("ix_research_tasks_id"), "research_tasks", ["id"], unique=False)
    op.create_index(
        op.f("ix_research_tasks_owner_id"), "research_tasks", ["owner_id"], unique=False
    )
    op.create_index(
        op.f("ix_research_tasks_project_id"), "research_tasks", ["project_id"], unique=False
    )
    op.create_index(
        op.f("ix_research_tasks_scope_id"), "research_tasks", ["scope_id"], unique=False
    )
    op.create_index(
        op.f("ix_research_tasks_workspace_id"),
        "research_tasks",
        ["workspace_id"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_research_tasks_workspace_id"), table_name="research_tasks")
    op.drop_index(op.f("ix_research_tasks_scope_id"), table_name="research_tasks")
    op.drop_index(op.f("ix_research_tasks_project_id"), table_name="research_tasks")
    op.drop_index(op.f("ix_research_tasks_owner_id"), table_name="research_tasks")
    op.drop_index(op.f("ix_research_tasks_id"), table_name="research_tasks")
    op.drop_index(op.f("ix_research_tasks_document_id"), table_name="research_tasks")
    op.drop_table("research_tasks")
