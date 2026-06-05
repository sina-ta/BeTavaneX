"""Readiness lineage event types (Runtime Hardening P2).

Revision ID: 20260603_0006
Revises: 20260603_0005
Create Date: 2026-06-05
"""

from typing import Sequence, Union

from alembic import op

revision: str = "20260603_0006"
down_revision: Union[str, None] = "20260603_0005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_EVENT_TYPE_CHECK = (
    "event_type IN ("
    "'approval_completed', "
    "'blocker_registered', "
    "'blocker_resolved', "
    "'daily_report_submitted', "
    "'dependency_edge_created', "
    "'dependency_edge_deactivated', "
    "'readiness_blocked', "
    "'readiness_evaluated', "
    "'readiness_recovered', "
    "'work_order_assigned'"
    ")"
)


def upgrade() -> None:
    op.drop_constraint(
        "operational_events_event_type_check",
        "operational_events",
        type_="check",
    )
    op.create_check_constraint(
        "operational_events_event_type_check",
        "operational_events",
        _EVENT_TYPE_CHECK,
    )


def downgrade() -> None:
    op.drop_constraint(
        "operational_events_event_type_check",
        "operational_events",
        type_="check",
    )
    op.create_check_constraint(
        "operational_events_event_type_check",
        "operational_events",
        (
            "event_type IN ("
            "'approval_completed', "
            "'blocker_registered', "
            "'blocker_resolved', "
            "'daily_report_submitted', "
            "'dependency_edge_created', "
            "'dependency_edge_deactivated', "
            "'work_order_assigned'"
            ")"
        ),
    )
