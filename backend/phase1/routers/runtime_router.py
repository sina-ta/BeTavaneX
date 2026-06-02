"""Runtime router: thin FastAPI surface over RuntimeUseCases.

Endpoints delegate to the application layer and return Read schemas or runtime
views. ORM models are never returned directly. No business logic, no
calculations, no repository access.
"""

from __future__ import annotations

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from backend.phase1.application.runtime_use_cases import RuntimeUseCases
from backend.phase1.dependencies.application import get_runtime_use_cases
from backend.phase1.schemas.activity_instance_schema import ActivityInstanceRead
from backend.phase1.schemas.approval_schema import (
    ApprovalRead,
    WorkflowStepApprovalCreate,
)
from backend.phase1.schemas.daily_report_schema import (
    DailyReportCreate,
    DailyReportRead,
)
from backend.phase1.schemas.work_order_workflow_step_schema import (
    WorkOrderAssignmentCreate,
    WorkOrderWorkflowStepRead,
)
from backend.phase1.schemas.workflow_step_schema import WorkflowStepRead

router = APIRouter(prefix="/runtime", tags=["runtime"])


@router.get("/projects/{project_id}/dashboard")
def get_project_dashboard(
    project_id: UUID,
    runtime: RuntimeUseCases = Depends(get_runtime_use_cases),
) -> dict[str, Any]:
    summary = runtime.get_project_dashboard(project_id)
    return dict(summary)


@router.get("/activity-instances/{activity_instance_id}")
def get_activity_instance(
    activity_instance_id: UUID,
    runtime: RuntimeUseCases = Depends(get_runtime_use_cases),
) -> dict[str, Any]:
    view = runtime.get_activity_instance_dashboard(activity_instance_id)
    activity_instance = view["activity_instance"]
    return {
        "activity_instance": (
            ActivityInstanceRead.model_validate(activity_instance)
            if activity_instance is not None
            else None
        ),
        "workflow_steps": [
            WorkflowStepRead.model_validate(step) for step in view["workflow_steps"]
        ],
        "progress_summary": view["progress_summary"],
    }


@router.post(
    "/work-orders/{work_order_id}/assign",
    response_model=WorkOrderWorkflowStepRead,
    status_code=status.HTTP_201_CREATED,
)
def assign_work_order(
    work_order_id: UUID,
    payload: WorkOrderAssignmentCreate,
    runtime: RuntimeUseCases = Depends(get_runtime_use_cases),
) -> WorkOrderWorkflowStepRead:
    try:
        return runtime.assign_work_order(
            work_order_id,
            payload.workflow_step_id,
            payload.execution_weight,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.post(
    "/daily-reports",
    response_model=DailyReportRead,
    status_code=status.HTTP_201_CREATED,
)
def submit_daily_report(
    payload: DailyReportCreate,
    runtime: RuntimeUseCases = Depends(get_runtime_use_cases),
) -> DailyReportRead:
    try:
        return runtime.submit_daily_report(
            payload.work_order_id,
            payload.report_date,
            status=payload.status,
            summary=payload.summary,
            execution_notes=payload.execution_notes,
            issue_notes=payload.issue_notes,
            delay_notes=payload.delay_notes,
            weather_notes=payload.weather_notes,
            evidence_metadata=payload.evidence_metadata,
            submitted_by=payload.submitted_by,
            submitted_at=payload.submitted_at,
            reported_manpower=payload.reported_manpower,
            reported_equipment=payload.reported_equipment,
            reported_material_entries=payload.reported_material_entries,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.post(
    "/workflow-steps/{workflow_step_id}/approve",
    response_model=ApprovalRead,
    status_code=status.HTTP_201_CREATED,
)
def approve_workflow_step(
    workflow_step_id: UUID,
    payload: WorkflowStepApprovalCreate,
    runtime: RuntimeUseCases = Depends(get_runtime_use_cases),
) -> ApprovalRead:
    try:
        return runtime.approve_workflow_step(
            workflow_step_id,
            approval_type=payload.approval_type,
            approved_by=payload.approved_by,
            approval_date=payload.approval_date,
            approval_notes=payload.approval_notes,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
