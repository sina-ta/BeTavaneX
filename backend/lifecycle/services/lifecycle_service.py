import json

from datetime import datetime

from backend.database import SessionLocal

from backend.repositories.report_repository import ReportRepository

from backend.lifecycle.repositories.lifecycle_repository import (
    LifecycleRepository,
)

from backend.lifecycle.validators.transition_validator import (
    validate_task_transition,
    validate_work_order_transition,
)

from backend.lifecycle.dependencies.dependency_engine import (
    evaluate_dependencies,
    map_dependency_to_readiness,
)

from backend.lifecycle.escalation.escalation_engine import (
    evaluate_escalation_triggers,
)

from backend.lifecycle.approvals.approval_engine import (
    build_approval_requests,
    can_approve_at_level,
)

from backend.lifecycle.models.entities import (
    OperationalBlocker,
    ExecutionDependency,
    ApprovalRequest,
    EscalationRecord,
)

from backend.lifecycle.utils.enums import (
    ApprovalStatus,
    TimelineEventType,
)


def _serialize_blocker(blocker: OperationalBlocker) -> dict:
    return {
        "id": blocker.id,
        "blocker_type": blocker.blocker_type,
        "severity": blocker.severity,
        "title": blocker.title,
        "description": blocker.description,
        "operational_impact": blocker.operational_impact,
        "expected_delay_days": blocker.expected_delay_days,
        "responsible_entity": blocker.responsible_entity,
        "resolution_state": blocker.resolution_state,
    }


def _serialize_dependency(dep: ExecutionDependency) -> dict:
    return {
        "id": dep.id,
        "dependency_type": dep.dependency_type,
        "depends_on_entity_type": dep.depends_on_entity_type,
        "depends_on_entity_id": dep.depends_on_entity_id,
        "is_satisfied": dep.is_satisfied,
        "description": dep.description,
    }


def get_task_lifecycle_service(task_id: int) -> dict:
    session = SessionLocal()

    try:
        repo = LifecycleRepository(session)
        work_order = repo.get_work_order_by_task(task_id)

        if not work_order:
            return {"error": "Task not found"}

        task_lc = repo.ensure_task_lifecycle(
            task_id,
            work_order.id,
        )
        wo_lc = repo.ensure_work_order_lifecycle(work_order)
        repo.commit()

        blockers = repo.get_blockers("task", task_id)
        dependencies = repo.get_dependencies("task", task_id)
        approvals = repo.get_approvals("task", task_id)
        escalations = repo.get_escalations("task", task_id)
        readiness = repo.get_latest_readiness("task", task_id)

        return {
            "task_id": task_id,
            "work_order_id": work_order.id,
            "task_state": task_lc.current_state,
            "work_order_state": wo_lc.current_state,
            "maturity_level": task_lc.maturity_level,
            "responsible_entity": task_lc.responsible_entity,
            "blockers": [_serialize_blocker(b) for b in blockers],
            "dependencies": [
                _serialize_dependency(d) for d in dependencies
            ],
            "approvals": [
                {
                    "id": a.id,
                    "level": a.approval_chain_level,
                    "required_role": a.required_role,
                    "status": a.status,
                }
                for a in approvals
            ],
            "escalations": [
                {
                    "id": e.id,
                    "trigger_type": e.trigger_type,
                    "escalation_level": e.escalation_level,
                    "severity": e.severity,
                    "resolution_state": e.resolution_state,
                }
                for e in escalations
            ],
            "readiness": {
                "status": readiness.readiness_status,
                "score": readiness.readiness_score,
            }
            if readiness
            else None,
        }
    finally:
        session.close()


def transition_task_state_service(
    task_id: int,
    to_state: str,
    triggered_by: str | None = None,
    reason: str | None = None,
) -> dict:
    session = SessionLocal()

    try:
        repo = LifecycleRepository(session)
        work_order = repo.get_work_order_by_task(task_id)

        if not work_order:
            return {"error": "Task not found"}

        task_lc = repo.ensure_task_lifecycle(
            task_id,
            work_order.id,
        )

        validation = validate_task_transition(
            task_lc.current_state,
            to_state,
        )

        if not validation["valid"]:
            return {"error": validation["message"]}

        from_state = task_lc.current_state
        task_lc.current_state = to_state
        task_lc.updated_at = datetime.utcnow()

        repo.record_transition(
            "task",
            task_id,
            from_state,
            to_state,
            triggered_by,
            reason,
        )

        repo.add_timeline_event(
            entity_type="task",
            entity_id=task_id,
            task_id=task_id,
            work_order_id=work_order.id,
            event_type=TimelineEventType.STATE_TRANSITION.value,
            title=f"Task → {to_state}",
            description=reason,
            recorded_by=triggered_by,
            payload={
                "from_state": from_state,
                "to_state": to_state,
            },
        )

        repo.commit()

        return {
            "task_id": task_id,
            "from_state": from_state,
            "to_state": to_state,
            "message": validation["message"],
        }
    finally:
        session.close()


def evaluate_task_readiness_service(task_id: int) -> dict:
    session = SessionLocal()

    try:
        repo = LifecycleRepository(session)
        work_order = repo.get_work_order_by_task(task_id)

        if not work_order:
            return {"error": "Task not found"}

        task_lc = repo.ensure_task_lifecycle(
            task_id,
            work_order.id,
        )

        blockers = repo.get_blockers("task", task_id)
        dependencies = repo.get_dependencies("task", task_id)
        approvals = repo.get_approvals("task", task_id)

        dep_result = evaluate_dependencies(dependencies, blockers)
        approval_pending = any(
            a.status == ApprovalStatus.PENDING.value
            for a in approvals
        )

        readiness = map_dependency_to_readiness(
            dep_result,
            approval_pending,
        )

        report_repo = ReportRepository(session)
        reports = report_repo.get_by_work_order_id(work_order.id)
        delay_count = len([
            r for r in reports
            if r.delay_reason and r.delay_reason.strip()
        ])

        escalations = evaluate_escalation_triggers(
            open_blocker_count=dep_result["open_blocker_count"],
            delay_count=delay_count,
            task_state=task_lc.current_state,
        )

        for esc in escalations:
            repo.session.add(
                EscalationRecord(
                    entity_type="task",
                    entity_id=task_id,
                    task_id=task_id,
                    work_order_id=work_order.id,
                    **esc,
                )
            )

        repo.save_readiness("task", task_id, task_id, readiness)

        repo.add_timeline_event(
            entity_type="task",
            entity_id=task_id,
            task_id=task_id,
            work_order_id=work_order.id,
            event_type=TimelineEventType.READINESS.value,
            title=f"Readiness: {readiness['status']}",
            description=f"Score {readiness['score']}",
            payload=readiness,
        )

        repo.commit()

        return {
            "task_id": task_id,
            **readiness,
            "dependency_summary": dep_result,
            "escalations_created": len(escalations),
        }
    finally:
        session.close()


def create_blocker_service(payload: dict) -> dict:
    session = SessionLocal()

    try:
        repo = LifecycleRepository(session)

        blocker = OperationalBlocker(
            entity_type=payload["entity_type"],
            entity_id=payload["entity_id"],
            task_id=payload.get("task_id"),
            work_order_id=payload.get("work_order_id"),
            blocker_type=payload["blocker_type"],
            severity=payload.get("severity", "medium"),
            title=payload["title"],
            description=payload.get("description"),
            operational_impact=payload.get("operational_impact"),
            expected_delay_days=payload.get("expected_delay_days"),
            responsible_entity=payload.get("responsible_entity"),
        )

        repo.session.add(blocker)
        repo.session.flush()

        repo.add_timeline_event(
            entity_type=payload["entity_type"],
            entity_id=payload["entity_id"],
            task_id=payload.get("task_id"),
            work_order_id=payload.get("work_order_id"),
            event_type=TimelineEventType.BLOCKER.value,
            title=payload["title"],
            description=payload.get("description"),
            severity=payload.get("severity"),
        )

        repo.commit()

        return _serialize_blocker(blocker)
    finally:
        session.close()


def request_approval_service(
    entity_type: str,
    entity_id: int,
    requested_by: str,
) -> dict:
    session = SessionLocal()

    try:
        repo = LifecycleRepository(session)
        requests = build_approval_requests(
            entity_type,
            entity_id,
            requested_by,
        )

        created = []

        for req in requests:
            record = ApprovalRequest(**req)
            repo.session.add(record)
            created.append(record)

        repo.session.flush()

        for record in created:
            repo.add_timeline_event(
                entity_type=entity_type,
                entity_id=entity_id,
                event_type=TimelineEventType.APPROVAL.value,
                title=f"Approval requested: {record.required_role}",
                description=f"Level {record.approval_chain_level}",
                recorded_by=requested_by,
            )

        repo.commit()

        return {
            "entity_type": entity_type,
            "entity_id": entity_id,
            "approvals": [
                {
                    "id": r.id,
                    "level": r.approval_chain_level,
                    "required_role": r.required_role,
                    "status": r.status,
                }
                for r in created
            ],
        }
    finally:
        session.close()


def decide_approval_service(
    approval_id: int,
    role: str,
    decision: str,
    decided_by: str,
    notes: str | None = None,
) -> dict:
    session = SessionLocal()

    try:
        repo = LifecycleRepository(session)

        approval = (
            repo.session.query(ApprovalRequest)
            .filter(ApprovalRequest.id == approval_id)
            .first()
        )

        if not approval:
            return {"error": "Approval not found"}

        all_approvals = repo.get_approvals(
            approval.entity_type,
            approval.entity_id,
        )

        if not can_approve_at_level(all_approvals, role):
            return {"error": "Not authorized at current approval level"}

        approval.status = decision
        approval.decided_by = decided_by
        approval.decision_notes = notes
        approval.decided_at = datetime.utcnow()

        repo.add_timeline_event(
            entity_type=approval.entity_type,
            entity_id=approval.entity_id,
            event_type=TimelineEventType.APPROVAL.value,
            title=f"Approval {decision}",
            description=notes,
            recorded_by=decided_by,
            payload={"approval_id": approval_id, "decision": decision},
        )

        repo.commit()

        return {
            "approval_id": approval_id,
            "status": approval.status,
            "decided_by": decided_by,
        }
    finally:
        session.close()


def get_timeline_service(
    entity_type: str,
    entity_id: int,
) -> list[dict]:
    session = SessionLocal()

    try:
        repo = LifecycleRepository(session)
        events = repo.get_timeline(entity_type, entity_id)

        return [
            {
                "id": event.id,
                "event_type": event.event_type,
                "title": event.title,
                "description": event.description,
                "severity": event.severity,
                "occurred_at": event.occurred_at.isoformat(),
                "payload": json.loads(event.payload or "{}"),
            }
            for event in events
        ]
    finally:
        session.close()


def get_lifecycle_summary_service() -> dict:
    session = SessionLocal()

    try:
        repo = LifecycleRepository(session)

        from backend.lifecycle.models.entities import (
            TaskLifecycle,
            WorkOrderLifecycle,
        )

        tasks = repo.session.query(TaskLifecycle).all()
        work_orders = repo.session.query(WorkOrderLifecycle).all()

        state_counts: dict[str, int] = {}
        for task in tasks:
            state_counts[task.current_state] = (
                state_counts.get(task.current_state, 0) + 1
            )

        open_blockers = (
            repo.session.query(OperationalBlocker)
            .filter(OperationalBlocker.resolution_state == "open")
            .count()
        )

        open_escalations = (
            repo.session.query(EscalationRecord)
            .filter(EscalationRecord.resolution_state == "open")
            .count()
        )

        return {
            "total_tasks_tracked": len(tasks),
            "total_work_orders_tracked": len(work_orders),
            "task_state_distribution": state_counts,
            "open_blockers": open_blockers,
            "open_escalations": open_escalations,
        }
    finally:
        session.close()
