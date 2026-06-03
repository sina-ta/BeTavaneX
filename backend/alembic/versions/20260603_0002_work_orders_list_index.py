"""Composite index for project-scoped work order lists.

Revision ID: 20260603_0002
Revises: 20260603_0001
Create Date: 2026-06-03
"""

from typing import Sequence, Union

from alembic import op

revision: str = "20260603_0002"
down_revision: Union[str, None] = "20260603_0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index(
        "idx_work_orders_project_planned_date",
        "work_orders",
        ["project_id", "planned_date"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "idx_work_orders_project_planned_date",
        table_name="work_orders",
    )
