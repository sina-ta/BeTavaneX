"""Application dependency providers.

The application layer (``RuntimeUseCases``) is assembled exclusively from the
service providers (Part 3). Routers should depend on these providers rather
than instantiating services or repositories themselves.

Providers wire objects only; they never execute business logic.
"""

from __future__ import annotations

from fastapi import Depends

from backend.phase1.application.runtime_use_cases import RuntimeUseCases
from backend.phase1.dependencies.services import (
    get_progress_service,
    get_runtime_query_service,
    get_workflow_execution_service,
    get_workflow_governance_service,
)
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
