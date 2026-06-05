"""Authoritative dependency edge taxonomy (Runtime Hardening P1).

Grounded in ``docs/cosc/dependency-semantics-stabilization.md``. Only dependency
types that require *explicit* edges are included here. Types already enforced by
FKs (containment), junction tables (coordination link), or analytics-only
interpretation (informational, coordination handoff) are intentionally excluded.

This module defines allowed values and the canonical semantics stamped onto each
edge at creation. P1 records semantics; it does not execute propagation.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

# --- Entity types (edge endpoints) ----------------------------------------------
ENTITY_WORKFLOW_STEP: Final = "workflow_step"
ENTITY_ACTIVITY_INSTANCE: Final = "activity_instance"
ENTITY_WORK_ORDER: Final = "work_order"

SUPPORTED_ENTITY_TYPES: Final[frozenset[str]] = frozenset(
    {
        ENTITY_WORKFLOW_STEP,
        ENTITY_ACTIVITY_INSTANCE,
        ENTITY_WORK_ORDER,
    },
)

# --- Dependency types (explicit-edge substrate only) --------------------------
DEPENDENCY_EXECUTION: Final = "execution_dependency"
DEPENDENCY_READINESS: Final = "readiness_dependency"
DEPENDENCY_RESOURCE: Final = "resource_dependency"
DEPENDENCY_SPATIAL: Final = "spatial_dependency"
DEPENDENCY_GOVERNANCE: Final = "governance_dependency"

SUPPORTED_DEPENDENCY_TYPES: Final[frozenset[str]] = frozenset(
    {
        DEPENDENCY_EXECUTION,
        DEPENDENCY_READINESS,
        DEPENDENCY_RESOURCE,
        DEPENDENCY_SPATIAL,
        DEPENDENCY_GOVERNANCE,
    },
)

# --- Authority levels (dependency-semantics-stabilization §0) -----------------
AUTHORITY_HARD: Final = "hard"
AUTHORITY_SOFT: Final = "soft"
AUTHORITY_ADVISORY: Final = "advisory"
AUTHORITY_OBSERVATIONAL: Final = "observational"

SUPPORTED_AUTHORITY_LEVELS: Final[frozenset[str]] = frozenset(
    {
        AUTHORITY_HARD,
        AUTHORITY_SOFT,
        AUTHORITY_ADVISORY,
        AUTHORITY_OBSERVATIONAL,
    },
)

# --- Blocking semantics (recorded, not enforced in P1) ------------------------
BLOCKING_NONE: Final = "none"
BLOCKING_DELETE_TIME: Final = "delete_time"
BLOCKING_CREATE_TIME: Final = "create_time"
BLOCKING_DUPLICATE_BLOCK: Final = "duplicate_block"
BLOCKING_STATE_TRANSITION: Final = "state_transition"

SUPPORTED_BLOCKING_SEMANTICS: Final[frozenset[str]] = frozenset(
    {
        BLOCKING_NONE,
        BLOCKING_DELETE_TIME,
        BLOCKING_CREATE_TIME,
        BLOCKING_DUPLICATE_BLOCK,
        BLOCKING_STATE_TRANSITION,
    },
)

# --- Propagation semantics (recorded, not executed in P1) ---------------------
PROPAGATION_NONE: Final = "none"
PROPAGATION_PULL_BOTTOM_UP: Final = "pull_bottom_up"
PROPAGATION_STEP_STATUS_ONLY: Final = "step_status_only"
PROPAGATION_DELETE_CASCADE_RESTRICT: Final = "delete_cascade_restrict"
PROPAGATION_EXECUTION_ELIGIBILITY: Final = "execution_eligibility"
PROPAGATION_SIGNAL_ONLY: Final = "signal_only"

SUPPORTED_PROPAGATION_SEMANTICS: Final[frozenset[str]] = frozenset(
    {
        PROPAGATION_NONE,
        PROPAGATION_PULL_BOTTOM_UP,
        PROPAGATION_STEP_STATUS_ONLY,
        PROPAGATION_DELETE_CASCADE_RESTRICT,
        PROPAGATION_EXECUTION_ELIGIBILITY,
        PROPAGATION_SIGNAL_ONLY,
    },
)

# --- Edge lifecycle -----------------------------------------------------------
EDGE_STATUS_ACTIVE: Final = "active"
EDGE_STATUS_DEACTIVATED: Final = "deactivated"

SUPPORTED_EDGE_STATUSES: Final[frozenset[str]] = frozenset(
    {
        EDGE_STATUS_ACTIVE,
        EDGE_STATUS_DEACTIVATED,
    },
)


@dataclass(frozen=True, slots=True)
class DependencyTypeSemantics:
    authority_level: str
    blocking_semantics: str
    propagation_semantics: str
    allowed_source_types: frozenset[str]
    allowed_target_types: frozenset[str]


# Canonical semantics per dependency type (stabilization doc §1 matrix + §2).
DEPENDENCY_TYPE_SEMANTICS: Final[dict[str, DependencyTypeSemantics]] = {
    DEPENDENCY_EXECUTION: DependencyTypeSemantics(
        authority_level=AUTHORITY_HARD,
        blocking_semantics=BLOCKING_NONE,
        propagation_semantics=PROPAGATION_PULL_BOTTOM_UP,
        allowed_source_types=frozenset(
            {ENTITY_WORKFLOW_STEP, ENTITY_ACTIVITY_INSTANCE},
        ),
        allowed_target_types=frozenset(
            {ENTITY_WORKFLOW_STEP, ENTITY_ACTIVITY_INSTANCE},
        ),
    ),
    DEPENDENCY_READINESS: DependencyTypeSemantics(
        authority_level=AUTHORITY_SOFT,
        blocking_semantics=BLOCKING_NONE,
        propagation_semantics=PROPAGATION_NONE,
        allowed_source_types=frozenset(
            {ENTITY_WORKFLOW_STEP, ENTITY_ACTIVITY_INSTANCE},
        ),
        allowed_target_types=frozenset(
            {ENTITY_WORKFLOW_STEP, ENTITY_ACTIVITY_INSTANCE},
        ),
    ),
    DEPENDENCY_RESOURCE: DependencyTypeSemantics(
        authority_level=AUTHORITY_SOFT,
        blocking_semantics=BLOCKING_NONE,
        propagation_semantics=PROPAGATION_NONE,
        allowed_source_types=frozenset({ENTITY_WORKFLOW_STEP}),
        allowed_target_types=frozenset({ENTITY_WORKFLOW_STEP}),
    ),
    DEPENDENCY_SPATIAL: DependencyTypeSemantics(
        authority_level=AUTHORITY_SOFT,
        blocking_semantics=BLOCKING_NONE,
        propagation_semantics=PROPAGATION_NONE,
        allowed_source_types=frozenset({ENTITY_ACTIVITY_INSTANCE}),
        allowed_target_types=frozenset({ENTITY_ACTIVITY_INSTANCE}),
    ),
    DEPENDENCY_GOVERNANCE: DependencyTypeSemantics(
        authority_level=AUTHORITY_HARD,
        blocking_semantics=BLOCKING_STATE_TRANSITION,
        propagation_semantics=PROPAGATION_STEP_STATUS_ONLY,
        allowed_source_types=frozenset({ENTITY_WORKFLOW_STEP}),
        allowed_target_types=frozenset({ENTITY_WORKFLOW_STEP}),
    ),
}

# Sequencing types where a direct reverse active edge is forbidden (integrity).
_SEQUENCING_TYPES: Final[frozenset[str]] = frozenset(
    {
        DEPENDENCY_EXECUTION,
        DEPENDENCY_READINESS,
        DEPENDENCY_GOVERNANCE,
        DEPENDENCY_SPATIAL,
    },
)


def is_sequencing_dependency_type(dependency_type: str) -> bool:
    return dependency_type in _SEQUENCING_TYPES


def semantics_for(dependency_type: str) -> DependencyTypeSemantics:
    if dependency_type not in DEPENDENCY_TYPE_SEMANTICS:
        msg = f"Unsupported dependency type: {dependency_type}"
        raise ValueError(msg)
    return DEPENDENCY_TYPE_SEMANTICS[dependency_type]
