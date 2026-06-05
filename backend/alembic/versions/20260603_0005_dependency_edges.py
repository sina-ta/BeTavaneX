"""Operational dependency edge substrate (Runtime Hardening P1).

Revision ID: 20260603_0005
Revises: 20260603_0004
Create Date: 2026-06-05
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "20260603_0005"
down_revision: Union[str, None] = "20260603_0004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_ENTITY_TYPE_CHECK = (
    "source_entity_type IN ('activity_instance', 'work_order', 'workflow_step') "
    "AND target_entity_type IN ('activity_instance', 'work_order', 'workflow_step')"
)

_DEPENDENCY_TYPE_CHECK = (
    "dependency_type IN ("
    "'execution_dependency', "
    "'governance_dependency', "
    "'readiness_dependency', "
    "'resource_dependency', "
    "'spatial_dependency'"
    ")"
)

_AUTHORITY_CHECK = (
    "authority_level IN ('advisory', 'hard', 'observational', 'soft')"
)

_BLOCKING_CHECK = (
    "blocking_semantics IN ("
    "'create_time', "
    "'delete_time', "
    "'duplicate_block', "
    "'none', "
    "'state_transition'"
    ")"
)

_PROPAGATION_CHECK = (
    "propagation_semantics IN ("
    "'delete_cascade_restrict', "
    "'execution_eligibility', "
    "'none', "
    "'pull_bottom_up', "
    "'signal_only', "
    "'step_status_only'"
    ")"
)

_STATUS_CHECK = "lifecycle_status IN ('active', 'deactivated')"

_EVENT_TYPE_CHECK = (
    "event_type IN ("
    "'approval_completed', "
    "'blocker_registered', "
    "'blocker_resolved', "
    "'daily_report_submitted', "
    "'dependency_edge_created', "
    "'dependency_edge_deactivated', "
    "'work_order_assigned'"
    ")"
)


def upgrade() -> None:
    op.create_table(
        "operational_dependency_edges",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("source_entity_type", sa.String(length=50), nullable=False),
        sa.Column("source_entity_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("target_entity_type", sa.String(length=50), nullable=False),
        sa.Column("target_entity_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("dependency_type", sa.String(length=80), nullable=False),
        sa.Column("authority_level", sa.String(length=30), nullable=False),
        sa.Column("blocking_semantics", sa.String(length=50), nullable=False),
        sa.Column("propagation_semantics", sa.String(length=50), nullable=False),
        sa.Column(
            "lifecycle_status",
            sa.String(length=20),
            server_default="active",
            nullable=False,
        ),
        sa.Column("created_by", sa.String(length=150), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column("deactivated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deactivated_by", sa.String(length=150), nullable=True),
        sa.Column("deactivation_reason", sa.Text(), nullable=True),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.CheckConstraint(_ENTITY_TYPE_CHECK, name="ode_entity_type_check"),
        sa.CheckConstraint(_DEPENDENCY_TYPE_CHECK, name="ode_dependency_type_check"),
        sa.CheckConstraint(_AUTHORITY_CHECK, name="ode_authority_level_check"),
        sa.CheckConstraint(_BLOCKING_CHECK, name="ode_blocking_semantics_check"),
        sa.CheckConstraint(_PROPAGATION_CHECK, name="ode_propagation_semantics_check"),
        sa.CheckConstraint(_STATUS_CHECK, name="ode_lifecycle_status_check"),
        sa.CheckConstraint(
            "source_entity_id != target_entity_id",
            name="ode_no_self_link_check",
        ),
        sa.ForeignKeyConstraint(
            ["project_id"],
            ["projects.id"],
            name="ode_project_id_fkey",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
        if_not_exists=True,
    )
    op.create_index(
        "idx_ode_project_id",
        "operational_dependency_edges",
        ["project_id"],
        if_not_exists=True,
    )
    op.create_index(
        "idx_ode_dependency_type",
        "operational_dependency_edges",
        ["dependency_type"],
        if_not_exists=True,
    )
    op.create_index(
        "idx_ode_lifecycle_status",
        "operational_dependency_edges",
        ["lifecycle_status"],
        if_not_exists=True,
    )
    op.create_index(
        "idx_ode_source",
        "operational_dependency_edges",
        ["source_entity_type", "source_entity_id"],
        if_not_exists=True,
    )
    op.create_index(
        "idx_ode_target",
        "operational_dependency_edges",
        ["target_entity_type", "target_entity_id"],
        if_not_exists=True,
    )
    op.create_index(
        "uq_ode_active_identity",
        "operational_dependency_edges",
        [
            "project_id",
            "source_entity_type",
            "source_entity_id",
            "target_entity_type",
            "target_entity_id",
            "dependency_type",
        ],
        unique=True,
        postgresql_where=sa.text("lifecycle_status = 'active'"),
        if_not_exists=True,
    )

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
            "'work_order_assigned'"
            ")"
        ),
    )

    op.drop_index("uq_ode_active_identity", table_name="operational_dependency_edges")
    op.drop_index("idx_ode_target", table_name="operational_dependency_edges")
    op.drop_index("idx_ode_source", table_name="operational_dependency_edges")
    op.drop_index("idx_ode_lifecycle_status", table_name="operational_dependency_edges")
    op.drop_index("idx_ode_dependency_type", table_name="operational_dependency_edges")
    op.drop_index("idx_ode_project_id", table_name="operational_dependency_edges")
    op.drop_table("operational_dependency_edges")
