"""Runtime router: thin FastAPI surface over RuntimeUseCases.



Endpoints delegate to the application layer and return Read schemas or runtime

views. ORM models are never returned directly. No business logic, no

calculations, no repository access.

"""



from __future__ import annotations



from datetime import date

from typing import Any, Literal

from uuid import UUID



from fastapi import APIRouter, Depends, HTTPException, Query, status



from backend.phase1.auth.auth import User

from backend.phase1.auth.dependencies import get_current_active_user

from backend.phase1.auth.operational_audit import (
    log_concurrency_conflict,
    log_operational_action,
)
from backend.phase1.exceptions import ConcurrencyConflictError

from backend.phase1.auth.project_access import ProjectAccessService

from backend.phase1.auth.role_policy import (

    require_daily_report_submitter,

    require_runtime_reader,

    require_work_order_assigner,

    require_workflow_approver,

)

from backend.phase1.application.runtime_use_cases import RuntimeUseCases

from backend.phase1.events.event_recording_service import EventRecordingService

from backend.phase1.dependencies.application import get_runtime_use_cases

from backend.phase1.dependencies.auth import get_project_access_service

from backend.phase1.dependencies.events import get_event_recording_service

from backend.phase1.schemas.activity_instance_schema import ActivityInstanceRead

from backend.phase1.schemas.approval_schema import (

    ApprovalRead,

    WorkflowStepApprovalCreate,

)

from backend.phase1.schemas.blocker_schema import BlockerRead

from backend.phase1.schemas.daily_report_schema import (

    DailyReportCreate,

    DailyReportRead,

)

from backend.phase1.schemas.pagination_schema import PaginatedResponse

from backend.phase1.schemas.project_schema import ProjectRead

from backend.phase1.schemas.runtime_query_schema import (
    ProjectDashboardSummaryRead,
    ProjectWorkflowStepBatchItemRead,
    WorkflowStepOperationalRead,
)

from backend.phase1.schemas.work_order_schema import WorkOrderRead

from backend.phase1.schemas.work_order_workflow_step_schema import (

    WorkOrderAssignmentCreate,

    WorkOrderWorkflowStepRead,

)

from backend.phase1.schemas.workflow_step_schema import WorkflowStepRead



router = APIRouter(prefix="/runtime", tags=["runtime"])



_DEFAULT_LIMIT = 50

_MAX_LIMIT = 200
_MAX_BATCH_LIMIT = 500





def _pagination(limit: int = Query(_DEFAULT_LIMIT, ge=1, le=_MAX_LIMIT)) -> int:

    return limit





def _offset(offset: int = Query(0, ge=0)) -> int:

    return offset





def _http_from_runtime_error(exc: Exception) -> HTTPException:

    if isinstance(exc, ConcurrencyConflictError):

        return HTTPException(

            status_code=status.HTTP_409_CONFLICT,

            detail=str(exc),

        )

    message = str(exc)

    if message.startswith("Duplicate"):

        return HTTPException(status_code=status.HTTP_409_CONFLICT, detail=message)

    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=message)





@router.get(

    "/projects",

    response_model=PaginatedResponse[ProjectRead],

    dependencies=[Depends(require_runtime_reader)],

)

def list_projects(

    name: str | None = Query(None, description="Filter by project name or code"),

    status: str | None = Query(None, description="Filter by project status"),

    planned_start_from: date | None = Query(None),

    planned_start_to: date | None = Query(None),

    planned_finish_from: date | None = Query(None),

    planned_finish_to: date | None = Query(None),

    sort_by: Literal["planned_start", "created_at"] = Query("created_at"),

    sort_dir: Literal["asc", "desc"] = Query("desc"),

    limit: int = Depends(_pagination),

    offset: int = Depends(_offset),

    runtime: RuntimeUseCases = Depends(get_runtime_use_cases),

    current_user: User = Depends(get_current_active_user),

) -> PaginatedResponse[ProjectRead]:

    result = runtime.list_projects(

        current_user,

        name=name,

        status=status,

        planned_start_from=planned_start_from,

        planned_start_to=planned_start_to,

        planned_finish_from=planned_finish_from,

        planned_finish_to=planned_finish_to,

        sort_by=sort_by,

        sort_dir=sort_dir,

        offset=offset,

        limit=limit,

    )

    return PaginatedResponse(

        items=[ProjectRead.model_validate(item) for item in result["items"]],

        total=result["total"],

        limit=limit,

        offset=offset,

    )





@router.get(

    "/projects/{project_id}/activity-instances",

    response_model=PaginatedResponse[ActivityInstanceRead],

    dependencies=[Depends(require_runtime_reader)],

)

def list_activity_instances(

    project_id: UUID,

    wbs_item_id: UUID | None = Query(None),

    location_id: UUID | None = Query(None),

    status: str | None = Query(None),

    sort_by: Literal["planned_start", "created_at"] = Query("created_at"),

    sort_dir: Literal["asc", "desc"] = Query("desc"),

    limit: int = Depends(_pagination),

    offset: int = Depends(_offset),

    runtime: RuntimeUseCases = Depends(get_runtime_use_cases),

    current_user: User = Depends(get_current_active_user),

    project_access: ProjectAccessService = Depends(get_project_access_service),

) -> PaginatedResponse[ActivityInstanceRead]:

    project_access.ensure_project_access(current_user, project_id)

    result = runtime.list_activity_instances(

        project_id,

        wbs_item_id=wbs_item_id,

        location_id=location_id,

        status=status,

        sort_by=sort_by,

        sort_dir=sort_dir,

        offset=offset,

        limit=limit,

    )

    return PaginatedResponse(

        items=[

            ActivityInstanceRead.model_validate(item) for item in result["items"]

        ],

        total=result["total"],

        limit=limit,

        offset=offset,

    )





@router.get(

    "/projects/{project_id}/work-orders",

    response_model=PaginatedResponse[WorkOrderRead],

    dependencies=[Depends(require_runtime_reader)],

)

def list_work_orders(

    project_id: UUID,

    status: str | None = Query(None),

    workflow_step_id: UUID | None = Query(None),

    planned_date_from: date | None = Query(None),

    planned_date_to: date | None = Query(None),

    sort_by: Literal["planned_date", "created_at"] = Query("planned_date"),

    sort_dir: Literal["asc", "desc"] = Query("desc"),

    limit: int = Depends(_pagination),

    offset: int = Depends(_offset),

    runtime: RuntimeUseCases = Depends(get_runtime_use_cases),

    current_user: User = Depends(get_current_active_user),

    project_access: ProjectAccessService = Depends(get_project_access_service),

) -> PaginatedResponse[WorkOrderRead]:

    project_access.ensure_project_access(current_user, project_id)

    result = runtime.list_work_orders(

        project_id,

        status=status,

        workflow_step_id=workflow_step_id,

        planned_date_from=planned_date_from,

        planned_date_to=planned_date_to,

        sort_by=sort_by,

        sort_dir=sort_dir,

        offset=offset,

        limit=limit,

    )

    return PaginatedResponse(

        items=[WorkOrderRead.model_validate(item) for item in result["items"]],

        total=result["total"],

        limit=limit,

        offset=offset,

    )





@router.get(

    "/activity-instances/{activity_instance_id}/workflow-steps",

    response_model=PaginatedResponse[WorkflowStepOperationalRead],

    dependencies=[Depends(require_runtime_reader)],

)

def list_workflow_steps(

    activity_instance_id: UUID,

    status: str | None = Query(None),

    ready: bool | None = Query(None),

    sort_by: Literal["planned_start", "progress_percent", "created_at"] = Query(

        "created_at",

    ),

    sort_dir: Literal["asc", "desc"] = Query("desc"),

    limit: int = Depends(_pagination),

    offset: int = Depends(_offset),

    runtime: RuntimeUseCases = Depends(get_runtime_use_cases),

    current_user: User = Depends(get_current_active_user),

    project_access: ProjectAccessService = Depends(get_project_access_service),

) -> PaginatedResponse[WorkflowStepOperationalRead]:

    activity_project_id = runtime.get_activity_instance_project_id(

        activity_instance_id,

    )

    if activity_project_id is not None:

        project_access.ensure_project_access(current_user, activity_project_id)

    result = runtime.list_workflow_steps(

        activity_instance_id,

        status=status,

        ready=ready,

        sort_by=sort_by,

        sort_dir=sort_dir,

        offset=offset,

        limit=limit,

    )

    return PaginatedResponse(

        items=[

            WorkflowStepOperationalRead(

                workflow_step=WorkflowStepRead.model_validate(row["workflow_step"]),

                approvals=[

                    ApprovalRead.model_validate(approval)

                    for approval in row["approvals"]

                ],

                blockers=[

                    BlockerRead.model_validate(blocker) for blocker in row["blockers"]

                ],

            )

            for row in result["items"]

        ],

        total=result["total"],

        limit=limit,

        offset=offset,

    )





@router.get(

    "/work-orders/{work_order_id}/daily-reports",

    response_model=PaginatedResponse[DailyReportRead],

    dependencies=[Depends(require_runtime_reader)],

)

def list_daily_reports(

    work_order_id: UUID,

    status: str | None = Query(None),

    report_date_from: date | None = Query(None),

    report_date_to: date | None = Query(None),

    sort_by: Literal["report_date", "created_at"] = Query("report_date"),

    sort_dir: Literal["asc", "desc"] = Query("desc"),

    limit: int = Depends(_pagination),

    offset: int = Depends(_offset),

    runtime: RuntimeUseCases = Depends(get_runtime_use_cases),

    current_user: User = Depends(get_current_active_user),

    project_access: ProjectAccessService = Depends(get_project_access_service),

) -> PaginatedResponse[DailyReportRead]:

    work_order_project_id = runtime.get_work_order_project_id(work_order_id)

    if work_order_project_id is not None:

        project_access.ensure_project_access(current_user, work_order_project_id)

    result = runtime.list_daily_reports(

        work_order_id,

        status=status,

        report_date_from=report_date_from,

        report_date_to=report_date_to,

        sort_by=sort_by,

        sort_dir=sort_dir,

        offset=offset,

        limit=limit,

    )

    return PaginatedResponse(

        items=[DailyReportRead.model_validate(item) for item in result["items"]],

        total=result["total"],

        limit=limit,

        offset=offset,

    )





@router.get(

    "/projects/{project_id}/dashboard-summary",

    response_model=ProjectDashboardSummaryRead,

    dependencies=[Depends(require_runtime_reader)],

)

def get_project_dashboard_summary(

    project_id: UUID,

    runtime: RuntimeUseCases = Depends(get_runtime_use_cases),

    current_user: User = Depends(get_current_active_user),

    project_access: ProjectAccessService = Depends(get_project_access_service),

) -> ProjectDashboardSummaryRead:

    project_access.ensure_project_access(current_user, project_id)

    summary = runtime.get_project_dashboard_summary(project_id)

    return ProjectDashboardSummaryRead.model_validate(summary)


@router.get(
    "/projects/{project_id}/workflow-steps-batch",
    response_model=PaginatedResponse[ProjectWorkflowStepBatchItemRead],
    dependencies=[Depends(require_runtime_reader)],
)
def list_project_workflow_steps_batch(
    project_id: UUID,
    status: str | None = Query(None),
    limit: int = Query(_DEFAULT_LIMIT, ge=1, le=_MAX_BATCH_LIMIT),
    offset: int = Depends(_offset),
    runtime: RuntimeUseCases = Depends(get_runtime_use_cases),
    current_user: User = Depends(get_current_active_user),
    project_access: ProjectAccessService = Depends(get_project_access_service),
) -> PaginatedResponse[ProjectWorkflowStepBatchItemRead]:
    project_access.ensure_project_access(current_user, project_id)
    result = runtime.list_project_workflow_steps_batch(
        project_id,
        status=status,
        offset=offset,
        limit=limit,
    )
    return PaginatedResponse(
        items=[
            ProjectWorkflowStepBatchItemRead(
                activity_instance_id=row["activity_instance_id"],
                activity_code=row["activity_code"],
                activity_name=row["activity_name"],
                workflow_step=WorkflowStepRead.model_validate(row["workflow_step"]),
                approvals=[
                    ApprovalRead.model_validate(item) for item in row["approvals"]
                ],
                blockers=[
                    BlockerRead.model_validate(item) for item in row["blockers"]
                ],
            )
            for row in result["items"]
        ],
        total=result["total"],
        limit=limit,
        offset=offset,
    )


@router.get(

    "/projects/{project_id}/dashboard",

    dependencies=[Depends(require_runtime_reader)],

)

def get_project_dashboard(

    project_id: UUID,

    runtime: RuntimeUseCases = Depends(get_runtime_use_cases),

    current_user: User = Depends(get_current_active_user),

    project_access: ProjectAccessService = Depends(get_project_access_service),

) -> dict[str, Any]:

    project_access.ensure_project_access(current_user, project_id)

    summary = runtime.get_project_dashboard(project_id)

    return dict(summary)





@router.get(

    "/activity-instances/{activity_instance_id}",

    dependencies=[Depends(require_runtime_reader)],

)

def get_activity_instance(

    activity_instance_id: UUID,

    runtime: RuntimeUseCases = Depends(get_runtime_use_cases),

    current_user: User = Depends(get_current_active_user),

    project_access: ProjectAccessService = Depends(get_project_access_service),

) -> dict[str, Any]:

    activity_project_id = runtime.get_activity_instance_project_id(

        activity_instance_id,

    )

    if activity_project_id is not None:

        project_access.ensure_project_access(current_user, activity_project_id)

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

    dependencies=[Depends(require_work_order_assigner)],

)

def assign_work_order(

    work_order_id: UUID,

    payload: WorkOrderAssignmentCreate,

    runtime: RuntimeUseCases = Depends(get_runtime_use_cases),

    current_user: User = Depends(get_current_active_user),

    project_access: ProjectAccessService = Depends(get_project_access_service),

    events: EventRecordingService = Depends(get_event_recording_service),

) -> WorkOrderWorkflowStepRead:

    work_order_project_id = runtime.get_work_order_project_id(work_order_id)

    if work_order_project_id is not None:

        project_access.ensure_project_access(current_user, work_order_project_id)

    try:

        assignment = runtime.assign_work_order(

            work_order_id,

            payload.workflow_step_id,

            payload.execution_weight,

        )

        if work_order_project_id is not None:

            project_access.grant_project_operational_team(work_order_project_id)

        log_operational_action(

            current_user,

            "assign_work_order",

            mutation_category="execution",

            project_id=work_order_project_id,

            resource_type="work_order",

            resource_id=work_order_id,

            detail={"workflow_step_id": str(payload.workflow_step_id)},

        )

        events.record_work_order_assigned(

            work_order_id=work_order_id,

            workflow_step_id=payload.workflow_step_id,

            execution_weight=payload.execution_weight,

            actor=current_user.username,

            project_id=work_order_project_id,

            metadata={"role": current_user.role},

        )

        return assignment

    except ConcurrencyConflictError as exc:

        log_concurrency_conflict(

            current_user,

            action="assign_work_order",

            resource_type="work_order",

            resource_id=work_order_id,

            project_id=work_order_project_id,

        )

        raise _http_from_runtime_error(exc) from exc

    except ValueError as exc:

        raise _http_from_runtime_error(exc) from exc





@router.post(

    "/daily-reports",

    response_model=DailyReportRead,

    status_code=status.HTTP_201_CREATED,

    dependencies=[Depends(require_daily_report_submitter)],

)

def submit_daily_report(

    payload: DailyReportCreate,

    runtime: RuntimeUseCases = Depends(get_runtime_use_cases),

    current_user: User = Depends(get_current_active_user),

    project_access: ProjectAccessService = Depends(get_project_access_service),

    events: EventRecordingService = Depends(get_event_recording_service),

) -> DailyReportRead:

    work_order_project_id = runtime.get_work_order_project_id(payload.work_order_id)

    if work_order_project_id is not None:

        project_access.ensure_project_access(current_user, work_order_project_id)

        project_access.grant_project_access(

            current_user.username,

            work_order_project_id,

        )

    try:

        report = runtime.submit_daily_report(

            payload.work_order_id,

            payload.report_date,

            expected_work_order_updated_at=payload.expected_work_order_updated_at,

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

        log_operational_action(

            current_user,

            "submit_daily_report",

            mutation_category="execution",

            project_id=work_order_project_id,

            resource_type="daily_report",

            resource_id=report.id,

            detail={"work_order_id": str(payload.work_order_id)},

        )

        events.record_daily_report_submitted(

            daily_report_id=report.id,

            work_order_id=payload.work_order_id,

            actor=current_user.username,

            report_status=report.status,

            project_id=work_order_project_id,

            metadata={"role": current_user.role},

        )

        return report

    except ConcurrencyConflictError as exc:

        log_concurrency_conflict(

            current_user,

            action="submit_daily_report",

            resource_type="work_order",

            resource_id=payload.work_order_id,

            project_id=work_order_project_id,

        )

        raise _http_from_runtime_error(exc) from exc

    except ValueError as exc:

        raise _http_from_runtime_error(exc) from exc





@router.post(

    "/workflow-steps/{workflow_step_id}/approve",

    response_model=ApprovalRead,

    status_code=status.HTTP_201_CREATED,

    dependencies=[Depends(require_workflow_approver)],

)

def approve_workflow_step(

    workflow_step_id: UUID,

    payload: WorkflowStepApprovalCreate,

    runtime: RuntimeUseCases = Depends(get_runtime_use_cases),

    current_user: User = Depends(get_current_active_user),

    project_access: ProjectAccessService = Depends(get_project_access_service),

    events: EventRecordingService = Depends(get_event_recording_service),

) -> ApprovalRead:

    step_project_id = runtime.get_workflow_step_project_id(workflow_step_id)

    if step_project_id is not None:

        project_access.ensure_project_access(current_user, step_project_id)

    try:

        approval = runtime.approve_workflow_step(

            workflow_step_id,

            approval_type=payload.approval_type,

            approved_by=payload.approved_by,

            approval_date=payload.approval_date,

            approval_notes=payload.approval_notes,

            expected_workflow_step_updated_at=payload.expected_workflow_step_updated_at,

        )

        log_operational_action(

            current_user,

            "approve_workflow_step",

            mutation_category="governance",

            project_id=step_project_id,

            resource_type="workflow_step",

            resource_id=workflow_step_id,

            detail={"approval_type": payload.approval_type},

        )

        events.record_approval_completed(

            workflow_step_id=workflow_step_id,

            approval_id=approval.id,

            approval_type=payload.approval_type,

            actor=current_user.username,

            project_id=step_project_id,

            metadata={"role": current_user.role},

        )

        return approval

    except ConcurrencyConflictError as exc:

        log_concurrency_conflict(

            current_user,

            action="approve_workflow_step",

            resource_type="workflow_step",

            resource_id=workflow_step_id,

            project_id=step_project_id,

        )

        raise _http_from_runtime_error(exc) from exc

    except ValueError as exc:

        raise _http_from_runtime_error(exc) from exc


