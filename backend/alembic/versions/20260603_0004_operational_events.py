"""Operational event ledger (immutable lineage foundation).

Revision ID: 20260603_0004
Revises: 20260603_0003
Create Date: 2026-06-05
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "20260603_0004"
down_revision: Union[str, None] = "20260603_0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_EVENT_TYPE_CHECK = (
    "event_type IN ("
    "'approval_completed', "
    "'blocker_registered', "
    "'blocker_resolved', "
    "'daily_report_submitted', "
    "'work_order_assigned'"
    ")"
)


def upgrade() -> None:
    op.create_table(
        "operational_events",
        sa.Column(
            "event_id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("event_type", sa.String(length=100), nullable=False),
        sa.Column("aggregate_type", sa.String(length=100), nullable=False),
        sa.Column("aggregate_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("actor", sa.String(length=150), nullable=False),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("causality_reference", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.CheckConstraint(
            _EVENT_TYPE_CHECK,
            name="operational_events_event_type_check",
        ),
        sa.PrimaryKeyConstraint("event_id"),
        if_not_exists=True,
    )
    op.create_index(
        "idx_operational_events_aggregate",
        "operational_events",
        ["aggregate_type", "aggregate_id"],
        if_not_exists=True,
    )
    op.create_index(
        "idx_operational_events_event_type",
        "operational_events",
        ["event_type"],
        if_not_exists=True,
    )
    op.create_index(
        "idx_operational_events_occurred_at",
        "operational_events",
        ["occurred_at"],
        if_not_exists=True,
    )
    op.create_index(
        "idx_operational_events_actor",
        "operational_events",
        ["actor"],
        if_not_exists=True,
    )
    op.create_index(
        "idx_operational_events_causality_reference",
        "operational_events",
        ["causality_reference"],
        if_not_exists=True,
    )


def downgrade() -> None:
    op.drop_index(
        "idx_operational_events_causality_reference",
        table_name="operational_events",
    )
    op.drop_index(
        "idx_operational_events_actor",
        table_name="operational_events",
    )
    op.drop_index(
        "idx_operational_events_occurred_at",
        table_name="operational_events",
    )
    op.drop_index(
        "idx_operational_events_event_type",
        table_name="operational_events",
    )
    op.drop_index(
        "idx_operational_events_aggregate",
        table_name="operational_events",
    )
    op.drop_table("operational_events")
