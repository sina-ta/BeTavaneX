from datetime import datetime

from sqlalchemy.orm import Session

from backend.models import DailyWorkOrder

from backend.lifecycle.models.entities import (
    TaskLifecycle,
    WorkOrderLifecycle,
    LifecycleTransition,
    OperationalBlocker,
    ExecutionDependency,
    ApprovalRequest,
    EscalationRecord,
    ExecutionReadiness,
    OperationalTimelineEvent,
)


class LifecycleRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_work_order(self, work_order_id: int) -> DailyWorkOrder | None:
        return (
            self.session.query(DailyWorkOrder)
            .filter(DailyWorkOrder.id == work_order_id)
            .first()
        )

    def get_work_order_by_task(
        self,
        task_id: int,
    ) -> DailyWorkOrder | None:
        return (
            self.session.query(DailyWorkOrder)
            .filter(DailyWorkOrder.task_id == task_id)
            .first()
        )

    def get_task_lifecycle(
        self,
        task_id: int,
    ) -> TaskLifecycle | None:
        return (
            self.session.query(TaskLifecycle)
            .filter(TaskLifecycle.task_id == task_id)
            .first()
        )

    def get_work_order_lifecycle(
        self,
        work_order_id: int,
    ) -> WorkOrderLifecycle | None:
        return (
            self.session.query(WorkOrderLifecycle)
            .filter(WorkOrderLifecycle.work_order_id == work_order_id)
            .first()
        )

    def ensure_task_lifecycle(
        self,
        task_id: int,
        work_order_id: int | None = None,
        initial_state: str = "planned",
    ) -> TaskLifecycle:
        existing = self.get_task_lifecycle(task_id)

        if existing:
            return existing

        record = TaskLifecycle(
            task_id=task_id,
            work_order_id=work_order_id,
            current_state=initial_state,
        )
        self.session.add(record)
        self.session.flush()
        return record

    def ensure_work_order_lifecycle(
        self,
        work_order: DailyWorkOrder,
    ) -> WorkOrderLifecycle:
        existing = self.get_work_order_lifecycle(work_order.id)

        if existing:
            return existing

        state_map = {
            "active": "active",
            "pending": "created",
            "completed": "completed",
        }
        initial = state_map.get(
            (work_order.status or "").lower(),
            "created",
        )

        record = WorkOrderLifecycle(
            work_order_id=work_order.id,
            task_id=work_order.task_id,
            current_state=initial,
            responsible_entity=work_order.assigned_to,
        )
        self.session.add(record)
        self.session.flush()
        return record

    def record_transition(
        self,
        entity_type: str,
        entity_id: int,
        from_state: str | None,
        to_state: str,
        triggered_by: str | None,
        reason: str | None,
    ) -> LifecycleTransition:
        transition = LifecycleTransition(
            entity_type=entity_type,
            entity_id=entity_id,
            from_state=from_state,
            to_state=to_state,
            triggered_by=triggered_by,
            reason=reason,
        )
        self.session.add(transition)
        self.session.flush()
        return transition

    def add_timeline_event(
        self,
        *,
        entity_type: str,
        entity_id: int,
        event_type: str,
        title: str,
        description: str | None = None,
        task_id: int | None = None,
        work_order_id: int | None = None,
        severity: str | None = None,
        payload: dict | None = None,
        recorded_by: str | None = None,
    ) -> OperationalTimelineEvent:
        event = OperationalTimelineEvent(
            entity_type=entity_type,
            entity_id=entity_id,
            task_id=task_id,
            work_order_id=work_order_id,
            event_type=event_type,
            title=title,
            description=description,
            severity=severity,
            payload=OperationalTimelineEvent.serialize_payload(
                payload
            ),
            recorded_by=recorded_by,
        )
        self.session.add(event)
        self.session.flush()
        return event

    def get_blockers(
        self,
        entity_type: str,
        entity_id: int,
    ) -> list[OperationalBlocker]:
        return (
            self.session.query(OperationalBlocker)
            .filter(OperationalBlocker.entity_type == entity_type)
            .filter(OperationalBlocker.entity_id == entity_id)
            .all()
        )

    def get_dependencies(
        self,
        entity_type: str,
        entity_id: int,
    ) -> list[ExecutionDependency]:
        return (
            self.session.query(ExecutionDependency)
            .filter(
                ExecutionDependency.dependent_entity_type
                == entity_type
            )
            .filter(
                ExecutionDependency.dependent_entity_id == entity_id
            )
            .all()
        )

    def get_approvals(
        self,
        entity_type: str,
        entity_id: int,
    ) -> list[ApprovalRequest]:
        return (
            self.session.query(ApprovalRequest)
            .filter(ApprovalRequest.entity_type == entity_type)
            .filter(ApprovalRequest.entity_id == entity_id)
            .order_by(ApprovalRequest.approval_chain_level)
            .all()
        )

    def get_escalations(
        self,
        entity_type: str,
        entity_id: int,
    ) -> list[EscalationRecord]:
        return (
            self.session.query(EscalationRecord)
            .filter(EscalationRecord.entity_type == entity_type)
            .filter(EscalationRecord.entity_id == entity_id)
            .all()
        )

    def get_timeline(
        self,
        entity_type: str,
        entity_id: int,
        limit: int = 50,
    ) -> list[OperationalTimelineEvent]:
        return (
            self.session.query(OperationalTimelineEvent)
            .filter(
                OperationalTimelineEvent.entity_type == entity_type
            )
            .filter(
                OperationalTimelineEvent.entity_id == entity_id
            )
            .order_by(OperationalTimelineEvent.occurred_at.desc())
            .limit(limit)
            .all()
        )

    def get_latest_readiness(
        self,
        entity_type: str,
        entity_id: int,
    ) -> ExecutionReadiness | None:
        return (
            self.session.query(ExecutionReadiness)
            .filter(ExecutionReadiness.entity_type == entity_type)
            .filter(ExecutionReadiness.entity_id == entity_id)
            .order_by(ExecutionReadiness.evaluated_at.desc())
            .first()
        )

    def save_readiness(
        self,
        entity_type: str,
        entity_id: int,
        task_id: int | None,
        result: dict,
    ) -> ExecutionReadiness:
        import json

        record = ExecutionReadiness(
            entity_type=entity_type,
            entity_id=entity_id,
            task_id=task_id,
            readiness_status=result["status"],
            readiness_score=result["score"],
            factors=json.dumps(result.get("factors", [])),
        )
        self.session.add(record)
        self.session.flush()
        return record

    def commit(self):
        self.session.commit()
