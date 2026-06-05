"""Operational event taxonomy.

The taxonomy is intentionally narrow: it covers only the five foundational
lineage events. Aggregate types reuse existing domain terminology — no new
operational concepts are introduced here.

To add an event type later: add the constant, register it in
``SUPPORTED_EVENT_TYPES`` (and ``EVENT_AGGREGATE_TYPE`` if it maps to a single
aggregate), and add the CHECK value in a new Alembic migration. No code in the
recorder, repository, or model needs structural change.
"""

from __future__ import annotations

from typing import Final

# --- Aggregate types (reuse domain vocabulary; no new concepts) ---------------
AGGREGATE_WORK_ORDER: Final = "work_order"
AGGREGATE_DAILY_REPORT: Final = "daily_report"
AGGREGATE_WORKFLOW_STEP: Final = "workflow_step"
AGGREGATE_BLOCKER: Final = "blocker"
AGGREGATE_DEPENDENCY_EDGE: Final = "dependency_edge"

AGGREGATE_TYPES: Final[frozenset[str]] = frozenset(
    {
        AGGREGATE_WORK_ORDER,
        AGGREGATE_DAILY_REPORT,
        AGGREGATE_WORKFLOW_STEP,
        AGGREGATE_BLOCKER,
        AGGREGATE_DEPENDENCY_EDGE,
    },
)

# --- Initial event types (the only ones implemented in this foundation) -------
EVENT_WORK_ORDER_ASSIGNED: Final = "work_order_assigned"
EVENT_DAILY_REPORT_SUBMITTED: Final = "daily_report_submitted"
EVENT_APPROVAL_COMPLETED: Final = "approval_completed"
EVENT_BLOCKER_REGISTERED: Final = "blocker_registered"
EVENT_BLOCKER_RESOLVED: Final = "blocker_resolved"
EVENT_DEPENDENCY_EDGE_CREATED: Final = "dependency_edge_created"
EVENT_DEPENDENCY_EDGE_DEACTIVATED: Final = "dependency_edge_deactivated"
EVENT_READINESS_EVALUATED: Final = "readiness_evaluated"
EVENT_READINESS_BLOCKED: Final = "readiness_blocked"
EVENT_READINESS_RECOVERED: Final = "readiness_recovered"

SUPPORTED_EVENT_TYPES: Final[frozenset[str]] = frozenset(
    {
        EVENT_WORK_ORDER_ASSIGNED,
        EVENT_DAILY_REPORT_SUBMITTED,
        EVENT_APPROVAL_COMPLETED,
        EVENT_BLOCKER_REGISTERED,
        EVENT_BLOCKER_RESOLVED,
        EVENT_DEPENDENCY_EDGE_CREATED,
        EVENT_DEPENDENCY_EDGE_DEACTIVATED,
        EVENT_READINESS_EVALUATED,
        EVENT_READINESS_BLOCKED,
        EVENT_READINESS_RECOVERED,
    },
)

# The aggregate an event is anchored to. Approval lineage anchors on the
# workflow step it governs (the step is the durable operational subject).
EVENT_AGGREGATE_TYPE: Final[dict[str, str]] = {
    EVENT_WORK_ORDER_ASSIGNED: AGGREGATE_WORK_ORDER,
    EVENT_DAILY_REPORT_SUBMITTED: AGGREGATE_DAILY_REPORT,
    EVENT_APPROVAL_COMPLETED: AGGREGATE_WORKFLOW_STEP,
    EVENT_BLOCKER_REGISTERED: AGGREGATE_BLOCKER,
    EVENT_BLOCKER_RESOLVED: AGGREGATE_BLOCKER,
    EVENT_DEPENDENCY_EDGE_CREATED: AGGREGATE_DEPENDENCY_EDGE,
    EVENT_DEPENDENCY_EDGE_DEACTIVATED: AGGREGATE_DEPENDENCY_EDGE,
    EVENT_READINESS_EVALUATED: AGGREGATE_WORKFLOW_STEP,
    EVENT_READINESS_BLOCKED: AGGREGATE_WORKFLOW_STEP,
    EVENT_READINESS_RECOVERED: AGGREGATE_WORKFLOW_STEP,
}


def is_supported_event_type(event_type: str) -> bool:
    return event_type in SUPPORTED_EVENT_TYPES
