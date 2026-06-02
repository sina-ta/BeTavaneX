"""Application dependency providers.

The application layer (``RuntimeUseCases``) is assembled exclusively from the
service providers (Part 3). Routers should depend on these providers rather
than instantiating services or repositories themselves.

Providers wire objects only; they never execute business logic.
"""

from __future__ import annotations

from fastapi import Depends

from backend.phase1.application.planning_use_cases import PlanningUseCases
from backend.phase1.application.runtime_use_cases import RuntimeUseCases
from backend.phase1.dependencies.repositories import (
    get_activity_instance_repository,
    get_location_repository,
    get_project_repository,
    get_wbs_item_repository,
    get_work_order_repository,
    get_workflow_step_repository,
)
from backend.phase1.dependencies.services import (
    get_progress_service,
    get_runtime_query_service,
    get_workflow_execution_service,
    get_workflow_governance_service,
)
from backend.phase1.repositories.activity_instance_repository import (
    ActivityInstanceRepository,
)
from backend.phase1.repositories.location_repository import LocationRepository
from backend.phase1.repositories.project_repository import ProjectRepository
from backend.phase1.repositories.wbs_item_repository import WBSItemRepository
from backend.phase1.repositories.work_order_repository import WorkOrderRepository
from backend.phase1.repositories.workflow_step_repository import WorkflowStepRepository
from backend.phase1.services.progress_service import ProgressService
from backend.phase1.services.runtime_query_service import RuntimeQueryService
from backend.phase1.services.workflow_execution_service import WorkflowExecutionService
from backend.phase1.services.workflow_governance_service import (
    WorkflowGovernanceService,
)


def get_runtime_use_cases(
    progress_service: ProgressService = Depends(get_progress_service),
    runtime_query_service: RuntimeQueryService = Depends(get_runtime_query_service),
    workflow_execution_service: WorkflowExecutionService = Depends(
        get_workflow_execution_service,
    ),
    workflow_governance_service: WorkflowGovernanceService = Depends(
        get_workflow_governance_service,
    ),
) -> RuntimeUseCases:
    return RuntimeUseCases(
        progress_service,
        runtime_query_service,
        workflow_execution_service,
        workflow_governance_service,
    )


def get_planning_use_cases(
    project_repository: ProjectRepository = Depends(get_project_repository),
    wbs_item_repository: WBSItemRepository = Depends(get_wbs_item_repository),
    location_repository: LocationRepository = Depends(get_location_repository),
    activity_instance_repository: ActivityInstanceRepository = Depends(
        get_activity_instance_repository,
    ),
    workflow_step_repository: WorkflowStepRepository = Depends(
        get_workflow_step_repository,
    ),
    work_order_repository: WorkOrderRepository = Depends(get_work_order_repository),
) -> PlanningUseCases:
    return PlanningUseCases(
        project_repository,
        wbs_item_repository,
        location_repository,
        activity_instance_repository,
        workflow_step_repository,
        work_order_repository,
    )
