"""Phase 1 baseline — project_memberships (legacy incremental; idempotent).

Revision ID: 20260603_0001
Revises: 20260603_0000
Create Date: 2026-06-03

Deployments that pre-date ``20260603_0000`` may already have core tables from
``phase1_init_schema.py``; ``if_not_exists`` avoids duplicate DDL errors.
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "20260603_0001"
down_revision: Union[str, None] = "20260603_0000"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "project_memberships",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("username", sa.String(length=150), nullable=False),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "granted_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["project_id"],
            ["projects.id"],
            name="project_memberships_project_id_fkey",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "username",
            "project_id",
            name="project_memberships_username_project_key",
        ),
        if_not_exists=True,
    )
    op.create_index(
        "idx_project_memberships_username",
        "project_memberships",
        ["username"],
        if_not_exists=True,
    )
    op.create_index(
        "idx_project_memberships_project_id",
        "project_memberships",
        ["project_id"],
        if_not_exists=True,
    )


def downgrade() -> None:
    op.drop_index("idx_project_memberships_project_id", table_name="project_memberships")
    op.drop_index("idx_project_memberships_username", table_name="project_memberships")
    op.drop_table("project_memberships")
