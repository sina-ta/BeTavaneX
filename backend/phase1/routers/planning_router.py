"""Planning router: thin FastAPI surface over PlanningUseCases.

Endpoints validate input via Pydantic schemas, delegate to the application
layer, and return Read schemas. No business logic, no repository access.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from backend.phase1.auth.auth import User
from backend.phase1.auth.dependencies import get_current_active_user
from backend.phase1.auth.operational_audit import log_operational_action
from backend.phase1.auth.project_access import ProjectAccessService
from backend.phase1.auth.role_policy import require_planning_actor
from backend.phase1.application.planning_use_cases import PlanningUseCases
from backend.phase1.dependencies.application import get_planning_use_cases
from backend.phase1.dependencies.auth import get_project_access_service
from backend.phase1.dependencies.services import get_readiness_derivation_service
from backend.phase1.readiness.authority import (
    ReadinessAuthorityError,
    reject_direct_ready_mutation,
)
from backend.phase1.services.readiness_derivation_service import (
    ReadinessDerivationService,
)
from backend.phase1.schemas.activity_instance_schema import (
    ActivityInstanceCreate,
    ActivityInstanceRead,
)
from backend.phase1.schemas.location_schema import LocationCreate, LocationRead
from backend.phase1.schemas.project_schema import ProjectCreate, ProjectRead
from backend.phase1.schemas.wbs_item_schema import WBSItemCreate, WBSItemRead
from backend.phase1.schemas.work_order_schema import WorkOrderCreate, WorkOrderRead
from backend.phase1.schemas.workflow_step_schema import (
    WorkflowStepCreate,
    WorkflowStepRead,
)

router = APIRouter(
    prefix="/planning",
    tags=["planning"],
    dependencies=[Depends(require_planning_actor)],
)


@router.post("/projects", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
def create_project(
    payload: ProjectCreate,
    planning: PlanningUseCases = Depends(get_planning_use_cases),
    current_user: User = Depends(get_current_active_user),
    project_access: ProjectAccessService = Depends(get_project_access_service),
) -> ProjectRead:
    project = planning.create_project(
        code=payload.code,
        name=payload.name,
        description=payload.description,
        status=payload.status,
        planned_start=payload.planned_start,
        planned_finish=payload.planned_finish,
    )
    project_access.register_new_project(project.id, current_user)
    log_operational_action(
        current_user,
        "create_project",
        mutation_category="planning",
        project_id=project.id,
        resource_type="project",
        resource_id=project.id,
    )
    return project


@router.post("/wbs-items", response_model=WBSItemRead, status_code=status.HTTP_201_CREATED)
def create_wbs_item(
    payload: WBSItemCreate,
    planning: PlanningUseCases = Depends(get_planning_use_cases),
    current_user: User = Depends(get_current_active_user),
    project_access: ProjectAccessService = Depends(get_project_access_service),
) -> WBSItemRead:
    project_access.ensure_project_access(current_user, payload.project_id)
    item = planning.create_wbs_item(
        payload.project_id,
        code=payload.code,
        name=payload.name,
        level=payload.level,
        parent_id=payload.parent_id,
        description=payload.description,
        status=payload.status,
    )
    log_operational_action(
        current_user,
        "create_wbs_item",
        mutation_category="planning",
        project_id=payload.project_id,
        resource_type="wbs_item",
        resource_id=item.id,
    )
    return item


@router.post("/locations", response_model=LocationRead, status_code=status.HTTP_201_CREATED)
def create_location(
    payload: LocationCreate,
    planning: PlanningUseCases = Depends(get_planning_use_cases),
    current_user: User = Depends(get_current_active_user),
    project_access: ProjectAccessService = Depends(get_project_access_service),
) -> LocationRead:
    project_access.ensure_project_access(current_user, payload.project_id)
    location = planning.create_location(
        payload.project_id,
        code=payload.code,
        name=payload.name,
        level=payload.level,
        parent_id=payload.parent_id,
        description=payload.description,
        status=payload.status,
    )
    log_operational_action(
        current_user,
        "create_location",
        mutation_category="planning",
        project_id=payload.project_id,
        resource_type="location",
        resource_id=location.id,
    )
    return location


@router.post(
    "/activity-instances",
    response_model=ActivityInstanceRead,
    status_code=status.HTTP_201_CREATED,
)
def create_activity_instance(
    payload: ActivityInstanceCreate,
    planning: PlanningUseCases = Depends(get_planning_use_cases),
    current_user: User = Depends(get_current_active_user),
    project_access: ProjectAccessService = Depends(get_project_access_service),
) -> ActivityInstanceRead:
    project_access.ensure_project_access(current_user, payload.project_id)
    instance = planning.create_activity_instance(
        payload.project_id,
        payload.wbs_item_id,
        payload.location_id,
        code=payload.code,
        name=payload.name,
        planned_start=payload.planned_start,
        planned_finish=payload.planned_finish,
        planned_duration_days=payload.planned_duration_days,
        status=payload.status,
    )
    log_operational_action(
        current_user,
        "create_activity_instance",
        mutation_category="planning",
        project_id=payload.project_id,
        resource_type="activity_instance",
        resource_id=instance.id,
    )
    return instance


@router.post(
    "/workflow-steps",
    response_model=WorkflowStepRead,
    status_code=status.HTTP_201_CREATED,
)
def create_workflow_step(
    payload: WorkflowStepCreate,
    planning: PlanningUseCases = Depends(get_planning_use_cases),
    readiness: ReadinessDerivationService = Depends(get_readiness_derivation_service),
    current_user: User = Depends(get_current_active_user),
    project_access: ProjectAccessService = Depends(get_project_access_service),
) -> WorkflowStepRead:
    activity_project_id = planning.get_activity_instance_project_id(
        payload.activity_instance_id,
    )
    if activity_project_id is not None:
        project_access.ensure_project_access(current_user, activity_project_id)
    try:
        reject_direct_ready_mutation(payload.ready)
    except ReadinessAuthorityError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    step = planning.create_workflow_step(
        payload.activity_instance_id,
        code=payload.code,
        name=payload.name,
        status=payload.status,
        workflow_template_id=payload.workflow_template_id,
        ready=False,
        progress_percent=payload.progress_percent,
        planned_weight=payload.planned_weight,
        planned_start=payload.planned_start,
        planned_finish=payload.planned_finish,
        actual_start=payload.actual_start,
        actual_finish=payload.actual_finish,
    )
    if activity_project_id is not None:
        readiness.initialize_workflow_step(
            step.id,
            activity_project_id,
            actor=current_user.username,
            trigger="workflow_step_created",
        )
        step = planning.get_workflow_step(step.id) or step

    log_operational_action(
        current_user,
        "create_workflow_step",
        mutation_category="planning",
        project_id=activity_project_id,
        resource_type="workflow_step",
        resource_id=step.id,
    )
    return step


@router.post("/work-orders", response_model=WorkOrderRead, status_code=status.HTTP_201_CREATED)
def create_work_order(
    payload: WorkOrderCreate,
    planning: PlanningUseCases = Depends(get_planning_use_cases),
    current_user: User = Depends(get_current_active_user),
    project_access: ProjectAccessService = Depends(get_project_access_service),
) -> WorkOrderRead:
    project_access.ensure_project_access(current_user, payload.project_id)
    work_order = planning.create_work_order(
        payload.project_id,
        work_order_number=payload.work_order_number,
        title=payload.title,
        planned_date=payload.planned_date,
        description=payload.description,
        status=payload.status,
        created_by=payload.created_by,
    )
    log_operational_action(
        current_user,
        "create_work_order",
        mutation_category="planning",
        project_id=payload.project_id,
        resource_type="work_order",
        resource_id=work_order.id,
    )
    return work_order
