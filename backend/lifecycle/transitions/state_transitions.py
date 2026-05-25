from backend.lifecycle.utils.enums import (
    TaskLifecycleState,
    WorkOrderLifecycleState,
)

TASK_TRANSITIONS: dict[str, set[str]] = {
    TaskLifecycleState.PLANNED.value: {
        TaskLifecycleState.READY.value,
        TaskLifecycleState.ARCHIVED.value,
    },
    TaskLifecycleState.READY.value: {
        TaskLifecycleState.ASSIGNED.value,
        TaskLifecycleState.BLOCKED.value,
        TaskLifecycleState.PLANNED.value,
    },
    TaskLifecycleState.ASSIGNED.value: {
        TaskLifecycleState.MOBILIZED.value,
        TaskLifecycleState.BLOCKED.value,
        TaskLifecycleState.DELAYED.value,
    },
    TaskLifecycleState.MOBILIZED.value: {
        TaskLifecycleState.IN_PROGRESS.value,
        TaskLifecycleState.BLOCKED.value,
    },
    TaskLifecycleState.IN_PROGRESS.value: {
        TaskLifecycleState.BLOCKED.value,
        TaskLifecycleState.DELAYED.value,
        TaskLifecycleState.UNDER_REVIEW.value,
        TaskLifecycleState.COMPLETED.value,
    },
    TaskLifecycleState.BLOCKED.value: {
        TaskLifecycleState.READY.value,
        TaskLifecycleState.IN_PROGRESS.value,
        TaskLifecycleState.DELAYED.value,
    },
    TaskLifecycleState.DELAYED.value: {
        TaskLifecycleState.IN_PROGRESS.value,
        TaskLifecycleState.BLOCKED.value,
    },
    TaskLifecycleState.UNDER_REVIEW.value: {
        TaskLifecycleState.COMPLETED.value,
        TaskLifecycleState.REJECTED.value,
        TaskLifecycleState.IN_PROGRESS.value,
    },
    TaskLifecycleState.COMPLETED.value: {
        TaskLifecycleState.VALIDATED.value,
        TaskLifecycleState.UNDER_REVIEW.value,
        TaskLifecycleState.REJECTED.value,
    },
    TaskLifecycleState.VALIDATED.value: {
        TaskLifecycleState.ARCHIVED.value,
    },
    TaskLifecycleState.REJECTED.value: {
        TaskLifecycleState.IN_PROGRESS.value,
        TaskLifecycleState.ARCHIVED.value,
    },
    TaskLifecycleState.ARCHIVED.value: set(),
}


WORK_ORDER_TRANSITIONS: dict[str, set[str]] = {
    WorkOrderLifecycleState.CREATED.value: {
        WorkOrderLifecycleState.APPROVED.value,
    },
    WorkOrderLifecycleState.APPROVED.value: {
        WorkOrderLifecycleState.ASSIGNED.value,
        WorkOrderLifecycleState.SUSPENDED.value,
    },
    WorkOrderLifecycleState.ASSIGNED.value: {
        WorkOrderLifecycleState.ACTIVE.value,
        WorkOrderLifecycleState.SUSPENDED.value,
    },
    WorkOrderLifecycleState.ACTIVE.value: {
        WorkOrderLifecycleState.SUSPENDED.value,
        WorkOrderLifecycleState.COMPLETED.value,
    },
    WorkOrderLifecycleState.SUSPENDED.value: {
        WorkOrderLifecycleState.ACTIVE.value,
        WorkOrderLifecycleState.ASSIGNED.value,
    },
    WorkOrderLifecycleState.COMPLETED.value: {
        WorkOrderLifecycleState.VALIDATED.value,
        WorkOrderLifecycleState.ACTIVE.value,
    },
    WorkOrderLifecycleState.VALIDATED.value: {
        WorkOrderLifecycleState.CLOSED.value,
    },
    WorkOrderLifecycleState.CLOSED.value: set(),
}


def can_transition_task(
    from_state: str,
    to_state: str,
) -> bool:
    allowed = TASK_TRANSITIONS.get(from_state, set())
    return to_state in allowed


def can_transition_work_order(
    from_state: str,
    to_state: str,
) -> bool:
    allowed = WORK_ORDER_TRANSITIONS.get(from_state, set())
    return to_state in allowed
