"""Runtime Core execution operations (links, reports, mappings)."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from backend.phase1.models.boq_mapping import BOQMapping
from backend.phase1.models.daily_report import DailyReport
from backend.phase1.models.work_order_workflow_step import WorkOrderWorkflowStep
from backend.phase1.repositories.boq_mapping_repository import BOQMappingRepository
from backend.phase1.repositories.daily_report_repository import DailyReportRepository
from backend.phase1.repositories.work_order_repository import WorkOrderRepository
from backend.phase1.auth.operational_alerts import alert_duplicate_assignment
from backend.phase1.repositories.optimistic import assert_unchanged
from backend.phase1.repositories.work_order_workflow_step_repository import (
    WorkOrderWorkflowStepRepository,
)
from backend.phase1.repositories.workflow_step_repository import WorkflowStepRepository


class WorkflowExecutionService:
    """Persistence-only runtime operations; no progress or workflow calculation."""

    def __init__(
        self,
        work_order_repository: WorkOrderRepository,
        workflow_step_repository: WorkflowStepRepository,
        daily_report_repository: DailyReportRepository,
        work_order_workflow_step_repository: WorkOrderWorkflowStepRepository,
        boq_mapping_repository: BOQMappingRepository,
    ) -> None:
        self._work_order_repository = work_order_repository
        self._workflow_step_repository = workflow_step_repository
        self._daily_report_repository = daily_report_repository
        self._work_order_workflow_step_repository = work_order_workflow_step_repository
        self._boq_mapping_repository = boq_mapping_repository

    def assign_work_order_to_workflow_step(
        self,
        work_order_id: UUID,
        workflow_step_id: UUID,
        execution_weight: Decimal,
    ) -> WorkOrderWorkflowStep:
        if self._work_order_repository.get_by_id(work_order_id) is None:
            msg = f"WorkOrder not found: {work_order_id}"
            raise ValueError(msg)
        if self._workflow_step_repository.get_by_id(workflow_step_id) is None:
            msg = f"WorkflowStep not found: {workflow_step_id}"
            raise ValueError(msg)

        existing = self._work_order_workflow_step_repository.get_by_work_order_and_step(
            work_order_id,
            workflow_step_id,
        )
        if existing is not None:
            alert_duplicate_assignment(
                work_order_id=work_order_id,
                workflow_step_id=workflow_step_id,
            )
            msg = (
                f"Duplicate assignment: work order {work_order_id} is already "
                f"linked to workflow step {workflow_step_id}"
            )
            raise ValueError(msg)

        assignment = WorkOrderWorkflowStep(
            work_order_id=work_order_id,
            workflow_step_id=workflow_step_id,
            execution_weight=execution_weight,
        )
        return self._work_order_workflow_step_repository.create(assignment)

    def remove_work_order_assignment(
        self,
        work_order_id: UUID,
        workflow_step_id: UUID,
    ) -> bool:
        assignment = self._work_order_workflow_step_repository.get_by_work_order_and_step(
            work_order_id,
            workflow_step_id,
        )
        if assignment is None:
            return False

        self._work_order_workflow_step_repository.delete(assignment)
        return True

    def create_daily_report(
        self,
        work_order_id: UUID,
        report_date: date,
        *,
        expected_work_order_updated_at: datetime | None = None,
        status: str = "DRAFT",
        summary: str | None = None,
        execution_notes: str | None = None,
        issue_notes: str | None = None,
        delay_notes: str | None = None,
        weather_notes: str | None = None,
        evidence_metadata: dict[str, Any] | list[Any] | None = None,
        submitted_by: UUID | None = None,
        submitted_at: datetime | None = None,
        reported_manpower: int | None = None,
        reported_equipment: int | None = None,
        reported_material_entries: int | None = None,
    ) -> DailyReport:
        work_order = self._work_order_repository.get_by_id(work_order_id)
        if work_order is None:
            msg = f"WorkOrder not found: {work_order_id}"
            raise ValueError(msg)

        assert_unchanged(
            resource_type="WorkOrder",
            resource_id=work_order_id,
            stored_updated_at=work_order.updated_at,
            expected_updated_at=expected_work_order_updated_at,
        )

        report = DailyReport(
            work_order_id=work_order_id,
            report_date=report_date,
            status=status,
            summary=summary,
            execution_notes=execution_notes,
            issue_notes=issue_notes,
            delay_notes=delay_notes,
            weather_notes=weather_notes,
            evidence_metadata=evidence_metadata,
            submitted_by=submitted_by,
            submitted_at=submitted_at,
            reported_manpower=reported_manpower,
            reported_equipment=reported_equipment,
            reported_material_entries=reported_material_entries,
        )
        return self._daily_report_repository.create(report)

    def link_boq_item(
        self,
        workflow_step_id: UUID,
        boq_item_id: UUID,
        allocated_quantity: Decimal,
        allocated_cost: Decimal,
        *,
        allocation_percentage: Decimal | None = None,
        notes: str | None = None,
    ) -> BOQMapping:
        if self._workflow_step_repository.get_by_id(workflow_step_id) is None:
            msg = f"WorkflowStep not found: {workflow_step_id}"
            raise ValueError(msg)

        mapping = BOQMapping(
            workflow_step_id=workflow_step_id,
            boq_item_id=boq_item_id,
            allocated_quantity=allocated_quantity,
            allocated_cost=allocated_cost,
            allocation_percentage=allocation_percentage,
            notes=notes,
        )
        return self._boq_mapping_repository.create(mapping)

    def unlink_boq_item(
        self,
        workflow_step_id: UUID,
        boq_item_id: UUID,
    ) -> bool:
        mapping = self._boq_mapping_repository.get_by_step_and_item(
            workflow_step_id,
            boq_item_id,
        )
        if mapping is None:
            return False

        self._boq_mapping_repository.delete(mapping)
        return True
