"""Explainable operational decision support (Stage 29) — deterministic, no ML."""

from __future__ import annotations

from collections import Counter
from datetime import date, datetime, timedelta, timezone
from typing import Any
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.phase1.analytics.audit_store import load_audit_records
from backend.phase1.analytics.operational_intelligence_service import (
    _approval_delay_days,
    _audit_action_count_project,
    _project_id_match,
    _stall_days,
    _utc_now,
    build_project_operational_intelligence,
)
from backend.phase1.models.activity_instance import ActivityInstance
from backend.phase1.models.approval import Approval
from backend.phase1.models.blocker import Blocker
from backend.phase1.models.daily_report import DailyReport
from backend.phase1.models.work_order import WorkOrder
from backend.phase1.models.workflow_step import WorkflowStep

_OPEN_BLOCKER = frozenset(
    {"OPEN", "ACKNOWLEDGED", "MITIGATION_IN_PROGRESS", "REOPENED"},
)
_PENDING_APPROVAL = frozenset({"PENDING", "UNDER_REVIEW"})
_INACTIVE_WO = frozenset({"CREATED", "ASSIGNED"})
_STALL_STEP = frozenset(
    {"IN_PROGRESS", "INSPECTION_PENDING", "REWORK_REQUIRED", "PLANNED"},
)


def _days_since(dt: datetime) -> int:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return max(0, (_utc_now() - dt).days)


def _empty_decision_support(project_id: UUID, *, note: str) -> dict[str, Any]:
    return {
        "project_id": str(project_id),
        "generated_at": _utc_now().isoformat(),
        "data_available": False,
        "priority_queue": [],
        "supervisor_guidance": [note],
        "approval_queue": [],
        "blocker_guidance": [],
        "workload_imbalance": [],
        "recommendations": [],
        "false_positive_notes": [
            "Priority scores use fixed thresholds (OPS_STALL_DAYS, OPS_APPROVAL_DELAY_DAYS).",
            "Workload imbalance uses audit JSONL when present; sparse logs reduce accuracy.",
            "Compare signals with Stage 28 health band before escalating.",
        ],
    }


def build_project_decision_support(
    db: Session | None,
    project_id: UUID,
) -> dict[str, Any]:
    """Deterministic decision support for one project."""
    intel = build_project_operational_intelligence(db, project_id)
    stall_days = intel.get("stall_threshold_days", _stall_days())
    approval_days = intel.get("approval_delay_threshold_days", _approval_delay_days())

    if db is None or not intel.get("data_available"):
        base = _empty_decision_support(
            project_id,
            note="Connect PostgreSQL for approval queues and priority ordering.",
        )
        base["recommendations"] = _recommendations_from_intel(intel, approval_days, stall_days)
        if intel.get("health", {}).get("band") == "AT_RISK":
            base["supervisor_guidance"].append(
                f"Project health is {intel['health']['band']}: "
                f"{intel['health'].get('summary', '')}",
            )
        return base

    try:
        return _build_decision_support_db(
            db,
            project_id,
            intel,
            stall_days,
            approval_days,
        )
    except Exception:  # noqa: BLE001
        base = _empty_decision_support(
            project_id,
            note="Could not compute decision support (query error).",
        )
        return base


def _build_decision_support_db(
    db: Session,
    project_id: UUID,
    intel: dict[str, Any],
    stall_days: int,
    approval_days: int,
) -> dict[str, Any]:
    now = _utc_now()
    stall_cutoff = now - timedelta(days=stall_days)
    approval_cutoff = now - timedelta(days=approval_days)
    report_cutoff = date.today() - timedelta(days=7)

    steps = db.execute(
        select(WorkflowStep, ActivityInstance)
        .join(
            ActivityInstance,
            WorkflowStep.activity_instance_id == ActivityInstance.id,
        )
        .where(ActivityInstance.project_id == project_id),
    ).all()

    pending_approvals = db.execute(
        select(Approval, WorkflowStep, ActivityInstance)
        .join(WorkflowStep, Approval.workflow_step_id == WorkflowStep.id)
        .join(ActivityInstance, WorkflowStep.activity_instance_id == ActivityInstance.id)
        .where(ActivityInstance.project_id == project_id)
        .where(Approval.status.in_(_PENDING_APPROVAL)),
    ).all()

    blockers = db.execute(
        select(Blocker, WorkflowStep, ActivityInstance)
        .join(WorkflowStep, Blocker.workflow_step_id == WorkflowStep.id)
        .join(ActivityInstance, WorkflowStep.activity_instance_id == ActivityInstance.id)
        .where(ActivityInstance.project_id == project_id),
    ).all()
    open_blockers = [(b, s, a) for b, s, a in blockers if b.status in _OPEN_BLOCKER]

    work_orders = db.scalars(
        select(WorkOrder).where(WorkOrder.project_id == project_id),
    ).all()

    reports_7d = (
        db.scalar(
            select(func.count())
            .select_from(DailyReport)
            .join(WorkOrder, DailyReport.work_order_id == WorkOrder.id)
            .where(WorkOrder.project_id == project_id)
            .where(DailyReport.report_date >= report_cutoff),
        )
        or 0
    )

    priority_items: list[dict[str, Any]] = []
    approval_queue: list[dict[str, Any]] = []

    for approval, step, act in sorted(
        pending_approvals,
        key=lambda row: row[0].updated_at,
    ):
        updated = approval.updated_at
        if updated.tzinfo is None:
            updated = updated.replace(tzinfo=timezone.utc)
        days_pending = _days_since(updated)
        overdue = updated < approval_cutoff
        score = 75 + min(20, days_pending) if overdue else 55 + min(10, days_pending)

        entry = {
            "queue_position": 0,
            "approval_id": str(approval.id),
            "workflow_step_id": str(step.id),
            "step_code": step.code,
            "activity_code": act.code,
            "approval_type": approval.approval_type,
            "status": approval.status,
            "days_pending": days_pending,
            "overdue": overdue,
            "priority_score": score,
            "explanation": (
                f"Pending {days_pending} day(s)"
                + (f" — exceeds {approval_days}-day threshold." if overdue else ".")
            ),
            "suggested_action": "Approve or reject to unblock downstream execution.",
        }
        approval_queue.append(entry)

        if overdue:
            priority_items.append(
                {
                    "category": "stalled_approval",
                    "priority_score": score,
                    "severity": "critical" if days_pending >= approval_days + 3 else "warning",
                    "title": f"Approval on {step.code} pending {days_pending} days",
                    "explanation": entry["explanation"],
                    "resource_type": "approval",
                    "resource_id": str(approval.id),
                    "workflow_step_id": str(step.id),
                    "suggested_action": entry["suggested_action"],
                },
            )

    for pos, item in enumerate(approval_queue, start=1):
        item["queue_position"] = pos

    for b, step, act in open_blockers:
        age = (date.today() - b.detected_date).days
        sev = b.severity
        score = 88 if sev in ("HIGH", "CRITICAL") else 72
        score += min(12, age)
        priority_items.append(
            {
                "category": "blocked_workflow",
                "priority_score": score,
                "severity": "critical" if sev in ("HIGH", "CRITICAL") else "warning",
                "title": f"Blocker ({sev}): {b.title}",
                "explanation": (
                    f"Open on step {step.code} ({act.code}); "
                    f"detected {age} day(s) ago; type {b.blocker_type}."
                ),
                "resource_type": "blocker",
                "resource_id": str(b.id),
                "workflow_step_id": str(step.id),
                "suggested_action": "Resolve or escalate blocker before new assignments.",
            },
        )

    for step, act in steps:
        updated = step.updated_at
        if updated.tzinfo is None:
            updated = updated.replace(tzinfo=timezone.utc)
        if step.status not in _STALL_STEP or updated >= stall_cutoff:
            continue
        days_idle = _days_since(updated)
        has_wo = any(wo.status not in ("COMPLETED", "CANCELLED") for wo in work_orders)
        score = 68 + min(15, days_idle)
        if has_wo:
            score += 5
        priority_items.append(
            {
                "category": "blocked_workflow",
                "priority_score": score,
                "severity": "warning",
                "title": f"Workflow {step.code} inactive ({step.status})",
                "explanation": (
                    f"No status change for {days_idle} day(s) in activity {act.name}."
                    + (" Work orders exist on project." if has_wo else "")
                ),
                "resource_type": "workflow_step",
                "resource_id": str(step.id),
                "workflow_step_id": str(step.id),
                "suggested_action": "Confirm field progress or reassign work order.",
            },
        )

    for wo in work_orders:
        updated = wo.updated_at
        if updated.tzinfo is None:
            updated = updated.replace(tzinfo=timezone.utc)
        if wo.status not in _INACTIVE_WO or updated >= stall_cutoff:
            continue
        days_idle = _days_since(updated)
        priority_items.append(
            {
                "category": "inactive_work_order",
                "priority_score": 48 + min(12, days_idle),
                "severity": "info",
                "title": f"Work order {wo.work_order_number} stuck in {wo.status}",
                "explanation": f"No movement for {days_idle} day(s).",
                "resource_type": "work_order",
                "resource_id": str(wo.id),
                "workflow_step_id": None,
                "suggested_action": "Assign to a workflow step or cancel if obsolete.",
            },
        )

    if reports_7d == 0 and len(work_orders) > 0:
        priority_items.append(
            {
                "category": "delayed_reporting",
                "priority_score": 42,
                "severity": "warning",
                "title": "No daily reports in the last 7 days",
                "explanation": f"{len(work_orders)} work order(s) on project without recent reports.",
                "resource_type": "project",
                "resource_id": str(project_id),
                "workflow_step_id": None,
                "suggested_action": "Ask field team to submit daily reports for active work orders.",
            },
        )

    rework = [s for s, _ in steps if s.status == "REWORK_REQUIRED"]
    if rework:
        step = rework[0]
        priority_items.append(
            {
                "category": "rework",
                "priority_score": 62,
                "severity": "warning",
                "title": f"{len(rework)} step(s) in REWORK_REQUIRED",
                "explanation": "Execution path reopened — approvals may be invalidated.",
                "resource_type": "workflow_step",
                "resource_id": str(step.id),
                "workflow_step_id": str(step.id),
                "suggested_action": "Review rework scope before approving new work.",
            },
        )

    priority_items.sort(key=lambda x: (-x["priority_score"], x["title"]))
    for rank, item in enumerate(priority_items[:20], start=1):
        item["rank"] = rank

    supervisor_guidance = _supervisor_guidance(
        pending_approvals,
        open_blockers,
        approval_days,
        intel,
        project_id,
    )
    blocker_guidance = _blocker_guidance(open_blockers, stall_days)
    workload = _workload_imbalance(project_id)
    recommendations = _recommendations_from_intel(
        intel,
        approval_days,
        stall_days,
        extra_context={
            "delayed_approval_count": sum(1 for a in approval_queue if a["overdue"]),
            "pending_approval_count": len(approval_queue),
            "reports_7d": reports_7d,
        },
    )

    return {
        "project_id": str(project_id),
        "generated_at": now.isoformat(),
        "data_available": True,
        "priority_queue": priority_items[:15],
        "supervisor_guidance": supervisor_guidance,
        "approval_queue": approval_queue[:15],
        "blocker_guidance": blocker_guidance,
        "workload_imbalance": workload,
        "recommendations": recommendations,
        "false_positive_notes": [
            "Priority score = base category weight + day-based increment (capped).",
            "Approval queue orders by oldest pending updated_at first.",
            "Supervisor workload uses audit JSONL; empty file skips imbalance detection.",
            "Align with Stage 28 health band and predictions before operational escalation.",
        ],
    }


def _supervisor_guidance(
    pending_approvals: list,
    open_blockers: list,
    approval_days: int,
    intel: dict[str, Any],
    project_id: UUID,
) -> list[str]:
    lines: list[str] = []
    overdue = 0
    for approval, _, _ in pending_approvals:
        updated = approval.updated_at
        if updated.tzinfo is None:
            updated = updated.replace(tzinfo=timezone.utc)
        if (_utc_now() - updated).days >= approval_days:
            overdue += 1

    if overdue:
        lines.append(
            f"{overdue} approval(s) delayed more than {approval_days} days — "
            "prioritize queue head before new assignments.",
        )
    elif len(pending_approvals) >= 5:
        lines.append(
            f"{len(pending_approvals)} pending approvals — "
            "supervisor queue may be overloaded.",
        )

    critical = sum(1 for b, _, _ in open_blockers if b.severity in ("HIGH", "CRITICAL"))
    if critical:
        lines.append(
            f"{critical} HIGH/CRITICAL blocker(s) open — "
            "field execution risk until resolved.",
        )
    if len(open_blockers) >= 3:
        lines.append(
            f"Blocker accumulation: {len(open_blockers)} open on this project.",
        )

    band = intel.get("health", {}).get("band")
    if band == "AT_RISK":
        lines.append(
            "Project health AT_RISK (Stage 28) — schedule a supervisor review this week.",
        )
    elif band == "ATTENTION":
        lines.append(
            "Project health ATTENTION — review stagnation signals on overview.",
        )

    inactive_wos = next(
        (
            s["count"]
            for s in intel.get("stagnation", [])
            if s.get("signal_type") == "inactive_work_orders"
        ),
        0,
    )
    if inactive_wos:
        lines.append(
            f"{inactive_wos} work order(s) inactive despite assignment capacity.",
        )

    approve_today = _audit_action_count_project(project_id, "approve", days=1)
    report_today = _audit_action_count_project(project_id, "submit", days=1)
    if approve_today >= 4 and report_today == 0:
        lines.append(
            "Approval activity today without matching report submissions — "
            "verify field reporting.",
        )

    if not lines:
        lines.append(
            "No supervisor escalation triggers at current thresholds — continue routine monitoring.",
        )
    return lines


def _blocker_guidance(
    open_blockers: list,
    stall_days: int,
) -> list[dict[str, Any]]:
    if not open_blockers:
        return []

    by_type: Counter[str] = Counter(b.blocker_type for b, _, _ in open_blockers)
    long_lived = []
    for b, step, act in open_blockers:
        age = (date.today() - b.detected_date).days
        if age >= stall_days:
            long_lived.append((age, b, step, act))

    guidance: list[dict[str, Any]] = []
    top = by_type.most_common(3)
    guidance.append(
        {
            "signal_type": "repeated_blocker_categories",
            "severity": "warning" if top[0][1] >= 2 else "info",
            "message": "Repeated blocker types: " + ", ".join(f"{k} ({v})" for k, v in top),
            "evidence": "Open blocker type distribution on project.",
            "count": len(open_blockers),
        },
    )
    if long_lived:
        longest = max(long_lived, key=lambda x: x[0])
        age, b, step, act = longest
        guidance.append(
            {
                "signal_type": "longest_unresolved_blocker",
                "severity": "critical" if age >= stall_days * 2 else "warning",
                "message": (
                    f"Longest open: \"{b.title}\" ({age} days) on {step.code} / {act.code}."
                ),
                "evidence": f"Threshold {stall_days} days for long-lived blockers.",
                "count": len(long_lived),
            },
        )
    if len(open_blockers) >= 4:
        guidance.append(
            {
                "signal_type": "rising_blocker_density",
                "severity": "warning",
                "message": f"{len(open_blockers)} simultaneous open blockers — execution hotspot.",
                "evidence": "Multiple concurrent open statuses.",
                "count": len(open_blockers),
            },
        )
    return guidance


def _workload_imbalance(project_id: UUID) -> list[dict[str, Any]]:
    cutoff = (_utc_now() - timedelta(days=7)).date().isoformat()
    by_user: Counter[str] = Counter()
    by_role: Counter[str] = Counter()
    actions: Counter[str] = Counter()

    for record in load_audit_records():
        if not _project_id_match(record, project_id):
            continue
        occurred = (record.get("occurred_at") or "")[:10]
        if occurred < cutoff:
            continue
        user = record.get("username") or "unknown"
        role = record.get("role") or "unknown"
        action = record.get("action") or ""
        by_user[user] += 1
        by_role[role] += 1
        if "approve" in action.lower():
            actions["approve"] += 1
        elif "submit" in action.lower() or "daily" in action.lower():
            actions["report"] += 1
        elif "assign" in action.lower():
            actions["assign"] += 1

    total = sum(by_user.values())
    if total < 3:
        return []

    findings: list[dict[str, Any]] = []
    if by_user:
        top_user, top_count = by_user.most_common(1)[0]
        share = top_count / total
        if share >= 0.7 and top_count >= 3:
            findings.append(
                {
                    "imbalance_type": "supervisor_concentration",
                    "severity": "warning",
                    "message": (
                        f"User '{top_user}' accounts for {int(share * 100)}% of "
                        f"project audit actions (7d)."
                    ),
                    "evidence": "May indicate single-supervisor overload or training gap.",
                    "metric": top_count,
                },
            )

    approve_n = actions.get("approve", 0)
    report_n = actions.get("report", 0)
    if approve_n >= 5 and report_n < approve_n // 2:
        findings.append(
            {
                "imbalance_type": "approval_vs_reporting",
                "severity": "warning",
                "message": (
                    f"Approvals ({approve_n}) dominate reporting ({report_n}) in last 7 days."
                ),
                "evidence": "Supervisor time on governance vs field capture.",
                "metric": approve_n,
            },
        )

    worker_actions = by_role.get("worker", 0)
    supervisor_actions = by_role.get("supervisor", 0) + by_role.get("admin", 0)
    if worker_actions == 0 and supervisor_actions >= 5:
        findings.append(
            {
                "imbalance_type": "neglected_field_activity",
                "severity": "info",
                "message": "No worker-role audit activity in 7 days despite planner activity.",
                "evidence": "Possible reporting gap or worker bypass.",
                "metric": supervisor_actions,
            },
        )

    return findings


def _recommendations_from_intel(
    intel: dict[str, Any],
    approval_days: int,
    stall_days: int,
    *,
    extra_context: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    ctx = extra_context or {}
    recs: list[dict[str, Any]] = []
    delayed = ctx.get("delayed_approval_count", 0)
    pending = ctx.get("pending_approval_count", 0)
    reports_7d = ctx.get("reports_7d")

    for signal in intel.get("approval_delays", []):
        if signal.get("signal_type") == "delayed_pending_approvals":
            delayed = max(delayed, signal.get("count", 0))

    if delayed >= 3:
        recs.append(
            {
                "severity": "critical",
                "message": (
                    f"Review stalled approvals ({delayed}) before approving new assignments."
                ),
                "rationale": f"Exceeds {approval_days}-day approval delay threshold (Stage 28/29).",
            },
        )
    elif delayed >= 1:
        recs.append(
            {
                "severity": "warning",
                "message": (
                    f"{delayed} approval(s) past threshold — clear queue head first."
                ),
                "rationale": "Deterministic approval-delay rule.",
            },
        )

    if pending >= 5:
        recs.append(
            {
                "severity": "warning",
                "message": f"Approval backlog ({pending} pending) — batch review recommended.",
                "rationale": "Queue depth heuristic.",
            },
        )

    for signal in intel.get("blocker_trends", []):
        if signal.get("severity") == "critical":
            recs.append(
                {
                    "severity": "critical",
                    "message": "Resolve critical blockers before expanding work order assignments.",
                    "rationale": signal.get("evidence", "Stage 28 blocker trend."),
                },
            )
            break

    if reports_7d is not None and reports_7d < 2:
        for comp in intel.get("health", {}).get("components", []):
            if comp.get("factor") == "reporting_gap":
                recs.append(
                    {
                        "severity": "warning",
                        "message": "Daily reporting frequency dropping — confirm field submission habit.",
                        "rationale": comp.get("detail", "No reports in 7 days."),
                    },
                )
                break

    band = intel.get("health", {}).get("band")
    if band == "AT_RISK":
        recs.append(
            {
                "severity": "critical",
                "message": "Project health AT_RISK — supervisor intervention recommended this week.",
                "rationale": intel.get("health", {}).get("summary", "Stage 28 health score."),
            },
        )

    for pred in intel.get("predictions", []):
        if pred.get("forecast") == "approval_backlog_risk" and len(recs) < 6:
            recs.append(
                {
                    "severity": "warning",
                    "message": "Approval backlog may grow — align supervisor capacity with pending queue.",
                    "rationale": pred.get("reason", "Stage 28 forecast."),
                },
            )

    seen: set[str] = set()
    unique: list[dict[str, Any]] = []
    for r in recs:
        key = r["message"]
        if key not in seen:
            seen.add(key)
            unique.append(r)
    return unique[:8]
