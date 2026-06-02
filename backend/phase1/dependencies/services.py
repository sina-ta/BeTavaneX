"""Service dependency providers.

Services are constructed exclusively from repository providers (Part 2). No
provider opens a Session directly or uses ``SessionLocal``; the shared
request-scoped Session arrives through the repository providers.

Providers wire objects only; they never execute business logic.
"""

from __future__ import annotations

from fastapi import Depends

from backend.phase1.dependencies.repositories import (
    get_activity_instance_repository,
    get_approval_repository,
    get_blocker_repository,
    get_boq_mapping_repository,
    get_daily_report_repository,
    get_inspection_repository,
    get_project_repository,
    get_work_order_repository,
    get_work_order_workflow_step_repository,
    get_workflow_step_repository,
)
from backend.phase1.repositories.activity_instance_repository import (
    ActivityInstanceRepository,
)
from backend.phase1.repositories.approval_repository import ApprovalRepository
from backend.phase1.repositories.blocker_repository import BlockerRepository
from backend.phase1.repositories.boq_mapping_repository import BOQMappingRepository
from backend.phase1.repositories.daily_report_repository import DailyReportRepository
from backend.phase1.repositories.inspection_repository import InspectionRepository
from backend.phase1.repositories.project_repository import ProjectRepository
from backend.phase1.repositories.work_order_repository import WorkOrderRepository
from backend.phase1.repositories.work_order_workflow_step_repository import (
    WorkOrderWorkflowStepRepository,
)
from backend.phase1.repositories.workflow_step_repository import WorkflowStepRepository
from backend.phase1.services.progress_service import ProgressService
from backend.phase1.services.runtime_query_service import RuntimeQueryService
from backend.phase1.services.workflow_execution_service import WorkflowExecutionService
from backend.phase1.services.workflow_governance_service import (
    WorkflowGovernanceService,
)


def get_progress_service(
    project_repository: ProjectRepository = Depends(get_project_repository),
    activity_instance_repository: ActivityInstanceRepository = Depends(
        get_activity_instance_repository,
    ),
    workflow_step_repository: WorkflowStepRepository = Depends(
        get_workflow_step_repository,
    ),
    work_order_repository: WorkOrderRepository = Depends(get_work_order_repository),
) -> ProgressService:
    return ProgressService(
        project_repository,
        activity_instance_repository,
        workflow_step_repository,
        work_order_repository,
    )


def get_runtime_query_service(
    activity_instance_repository: ActivityInstanceRepository = Depends(
        get_activity_instance_repository,
    ),
    workflow_step_repository: WorkflowStepRepository = Depends(
        get_workflow_step_repository,
    ),
    work_order_repository: WorkOrderRepository = Depends(get_work_order_repository),
    daily_report_repository: DailyReportRepository = Depends(
        get_daily_report_repository,
    ),
    inspection_repository: InspectionRepository = Depends(get_inspection_repository),
    approval_repository: ApprovalRepository = Depends(get_approval_repository),
    blocker_repository: BlockerRepository = Depends(get_blocker_repository),
    boq_mapping_repository: BOQMappingRepository = Depends(get_boq_mapping_repository),
    progress_service: ProgressService = Depends(get_progress_service),
) -> RuntimeQueryService:
    return RuntimeQueryService(
        activity_instance_repository,
        workflow_step_repository,
        work_order_repository,
        daily_report_repository,
        inspection_repository,
        approval_repository,
        blocker_repository,
        boq_mapping_repository,
        progress_service,
    )


def get_workflow_execution_service(
    work_order_repository: WorkOrderRepository = Depends(get_work_order_repository),
    workflow_step_repository: WorkflowStepRepository = Depends(
        get_workflow_step_repository,
    ),
    daily_report_repository: DailyReportRepository = Depends(
        get_daily_report_repository,
    ),
    work_order_workflow_step_repository: WorkOrderWorkflowStepRepository = Depends(
        get_work_order_workflow_step_repository,
    ),
    boq_mapping_repository: BOQMappingRepository = Depends(get_boq_mapping_repository),
) -> WorkflowExecutionService:
    return WorkflowExecutionService(
        work_order_repository,
        workflow_step_repository,
        daily_report_repository,
        work_order_workflow_step_repository,
        boq_mapping_repository,
    )


def get_workflow_governance_service(
    workflow_step_repository: WorkflowStepRepository = Depends(
        get_workflow_step_repository,
    ),
    approval_repository: ApprovalRepository = Depends(get_approval_repository),
    blocker_repository: BlockerRepository = Depends(get_blocker_repository),
) -> WorkflowGovernanceService:
    return WorkflowGovernanceService(
        workflow_step_repository,
        approval_repository,
        blocker_repository,
    )
