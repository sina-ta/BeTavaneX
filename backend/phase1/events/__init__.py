"""Operational event ledger (immutable lineage foundation).

This package provides lightweight, append-only operational lineage that coexists
with the state-oriented architecture. It is NOT event sourcing: current state
remains owned by the domain tables. See ``docs/cosc/event-ledger-foundation.md``.
"""

from backend.phase1.events.taxonomy import (
    AGGREGATE_DEPENDENCY_EDGE,
    AGGREGATE_TYPES,
    EVENT_APPROVAL_COMPLETED,
    EVENT_BLOCKER_REGISTERED,
    EVENT_BLOCKER_RESOLVED,
    EVENT_DAILY_REPORT_SUBMITTED,
    EVENT_DEPENDENCY_EDGE_CREATED,
    EVENT_DEPENDENCY_EDGE_DEACTIVATED,
    EVENT_READINESS_BLOCKED,
    EVENT_READINESS_EVALUATED,
    EVENT_READINESS_RECOVERED,
    EVENT_WORK_ORDER_ASSIGNED,
    SUPPORTED_EVENT_TYPES,
)

__all__ = [
    "AGGREGATE_DEPENDENCY_EDGE",
    "AGGREGATE_TYPES",
    "EVENT_APPROVAL_COMPLETED",
    "EVENT_BLOCKER_REGISTERED",
    "EVENT_BLOCKER_RESOLVED",
    "EVENT_DAILY_REPORT_SUBMITTED",
    "EVENT_DEPENDENCY_EDGE_CREATED",
    "EVENT_DEPENDENCY_EDGE_DEACTIVATED",
    "EVENT_READINESS_BLOCKED",
    "EVENT_READINESS_EVALUATED",
    "EVENT_READINESS_RECOVERED",
    "EVENT_WORK_ORDER_ASSIGNED",
    "SUPPORTED_EVENT_TYPES",
]
