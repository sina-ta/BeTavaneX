from fastapi import APIRouter

from backend.lifecycle.schemas.lifecycle import (
    TaskTransitionRequest,
    BlockerCreateRequest,
    ApprovalRequestPayload,
    ApprovalDecisionPayload,
)

from backend.lifecycle.services.lifecycle_service import (
    get_task_lifecycle_service,
    transition_task_state_service,
    evaluate_task_readiness_service,
    create_blocker_service,
    request_approval_service,
    decide_approval_service,
    get_timeline_service,
    get_lifecycle_summary_service,
)

router = APIRouter(prefix="/lifecycle", tags=["lifecycle"])


@router.get("/summary")
def lifecycle_summary():
    return get_lifecycle_summary_service()


@router.get("/tasks/{task_id}")
def get_task_lifecycle(task_id: int):
    return get_task_lifecycle_service(task_id)


@router.post("/tasks/{task_id}/transition")
def transition_task(
    task_id: int,
    payload: TaskTransitionRequest,
):
    return transition_task_state_service(
        task_id,
        payload.to_state,
        payload.triggered_by,
        payload.reason,
    )


@router.get("/tasks/{task_id}/readiness")
def task_readiness(task_id: int):
    return evaluate_task_readiness_service(task_id)


@router.get("/tasks/{task_id}/timeline")
def task_timeline(task_id: int):
    return get_timeline_service("task", task_id)


@router.post("/blockers")
def create_blocker(payload: BlockerCreateRequest):
    return create_blocker_service(payload.model_dump())


@router.post("/approvals/request")
def request_approval(payload: ApprovalRequestPayload):
    return request_approval_service(
        payload.entity_type,
        payload.entity_id,
        payload.requested_by,
    )


@router.post("/approvals/{approval_id}/decide")
def decide_approval(
    approval_id: int,
    payload: ApprovalDecisionPayload,
):
    return decide_approval_service(
        approval_id,
        payload.role,
        payload.decision,
        payload.decided_by,
        payload.notes,
    )
