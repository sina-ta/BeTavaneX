"""Runtime governance: WorkflowStep status, approvals, and blocker lifecycle."""

from __future__ import annotations

from datetime import date, datetime
from uuid import UUID

from backend.phase1.models.approval import Approval
from backend.phase1.models.blocker import Blocker
from backend.phase1.models.workflow_step import WorkflowStep
from backend.phase1.repositories.approval_repository import ApprovalRepository
from backend.phase1.repositories.blocker_repository import BlockerRepository
from backend.phase1.auth.operational_alerts import alert_duplicate_approval
from backend.phase1.repositories.workflow_step_repository import WorkflowStepRepository

_STATUS_INSPECTION_PENDING = "INSPECTION_PENDING"
_STATUS_INSPECTION_FAILED = "INSPECTION_FAILED"
_STATUS_REWORK_REQUIRED = "REWORK_REQUIRED"
_STATUS_APPROVED = "APPROVED"

_APPROVAL_STATUS_APPROVED = "APPROVED"
_BLOCKER_STATUS_OPEN = "OPEN"
_BLOCKER_STATUS_RESOLVED = "RESOLVED"


class WorkflowGovernanceService:
    """Governs runtime state transitions; no progress, reporting, or execution."""

    def __init__(
        self,
        workflow_step_repository: WorkflowStepRepository,
        approval_repository: ApprovalRepository,
        blocker_repository: BlockerRepository,
    ) -> None:
        self._workflow_step_repository = workflow_step_repository
        self._approval_repository = approval_repository
        self._blocker_repository = blocker_repository

    def mark_inspection_passed(self, workflow_step_id: UUID) -> WorkflowStep:
        workflow_step = self._require_step(workflow_step_id)
        if workflow_step.status != _STATUS_INSPECTION_PENDING:
            msg = (
                "WorkflowStep must be INSPECTION_PENDING to pass inspection; "
                f"current status: {workflow_step.status}"
            )
            raise ValueError(msg)
        workflow_step.status = _STATUS_APPROVED
        return self._workflow_step_repository.update(workflow_step)

    def mark_inspection_failed(self, workflow_step_id: UUID) -> WorkflowStep:
        workflow_step = self._require_step(workflow_step_id)
        workflow_step.status = _STATUS_INSPECTION_FAILED
        return self._workflow_step_repository.update(workflow_step)

    def require_rework(self, workflow_step_id: UUID) -> WorkflowStep:
        workflow_step = self._require_step(workflow_step_id)
        workflow_step.status = _STATUS_REWORK_REQUIRED
        return self._workflow_step_repository.update(workflow_step)

    def approve_workflow_step(
        self,
        workflow_step_id: UUID,
        *,
        approval_type: str = "FINAL",
        approved_by: UUID | None = None,
        approval_date: date | None = None,
        approval_notes: str | None = None,
        expected_workflow_step_updated_at: datetime | None = None,
    ) -> Approval:
        workflow_step = self._require_step(workflow_step_id)

        for existing in self._approval_repository.list(workflow_step_id=workflow_step_id):
            if (
                existing.approval_type == approval_type
                and existing.status == _APPROVAL_STATUS_APPROVED
            ):
                alert_duplicate_approval(
                    workflow_step_id=workflow_step_id,
                    approval_type=approval_type,
                )
                msg = (
                    f"Duplicate approval: workflow step {workflow_step_id} already has "
                    f"approved record of type {approval_type}"
                )
                raise ValueError(msg)

        approval = Approval(
            workflow_step_id=workflow_step_id,
            approval_type=approval_type,
            status=_APPROVAL_STATUS_APPROVED,
            approval_date=approval_date,
            approved_by=approved_by,
            approval_notes=approval_notes,
        )
        created = self._approval_repository.create(approval)

        workflow_step.status = _STATUS_APPROVED
        self._workflow_step_repository.update(
            workflow_step,
            expected_updated_at=expected_workflow_step_updated_at,
            resource_type="WorkflowStep",
        )

        return created

    def add_blocker(
        self,
        workflow_step_id: UUID,
        title: str,
        blocker_type: str,
        severity: str,
        detected_date: date,
        *,
        status: str = _BLOCKER_STATUS_OPEN,
        description: str | None = None,
        reported_by: UUID | None = None,
        root_cause: str | None = None,
    ) -> Blocker:
        self._require_step(workflow_step_id)

        blocker = Blocker(
            workflow_step_id=workflow_step_id,
            title=title,
            description=description,
            blocker_type=blocker_type,
            severity=severity,
            status=status,
            detected_date=detected_date,
            reported_by=reported_by,
            root_cause=root_cause,
        )
        return self._blocker_repository.create(blocker)

    def resolve_blocker(
        self,
        blocker_id: UUID,
        *,
        resolved_date: date | None = None,
        resolution_notes: str | None = None,
    ) -> Blocker:
        blocker = self._blocker_repository.get_by_id(blocker_id)
        if blocker is None:
            msg = f"Blocker not found: {blocker_id}"
            raise ValueError(msg)

        blocker.status = _BLOCKER_STATUS_RESOLVED
        blocker.resolved_date = resolved_date
        if resolution_notes is not None:
            blocker.resolution_notes = resolution_notes

        updated = self._blocker_repository.update(
            blocker,
            resource_type="Blocker",
        )
        return updated

    def _require_step(self, workflow_step_id: UUID) -> WorkflowStep:
        workflow_step = self._workflow_step_repository.get_by_id(workflow_step_id)
        if workflow_step is None:
            msg = f"WorkflowStep not found: {workflow_step_id}"
            raise ValueError(msg)
        return workflow_step
