"""Explainable team coordination intelligence (Stage 30) — heuristics only, no orchestration."""

from __future__ import annotations

from collections import Counter, defaultdict
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from typing import Any
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.phase1.analytics.operational_intelligence_service import (
    _approval_delay_days,
    _audit_action_count_project,
    _audit_conflicts_for_project,
    _PENDING_APPROVAL,
    _stall_days,
    _utc_now,
    build_project_operational_intelligence,
)

_OPEN_BLOCKER = frozenset(
    {"OPEN", "ACKNOWLEDGED", "MITIGATION_IN_PROGRESS", "REOPENED"},
)
from backend.phase1.models.activity_instance import ActivityInstance
from backend.phase1.models.approval import Approval
from backend.phase1.models.blocker import Blocker
from backend.phase1.models.daily_report import DailyReport
from backend.phase1.models.work_order import WorkOrder
from backend.phase1.models.workflow_step import WorkflowStep

_INACTIVE_WO = frozenset({"CREATED", "ASSIGNED"})
_STALL_STEP = frozenset(
    {"IN_PROGRESS", "INSPECTION_PENDING", "REWORK_REQUIRED", "PLANNED"},
)


def _empty_coordination(project_id: UUID, note: str) -> dict[str, Any]:
    return {
        "project_id": str(project_id),
        "generated_at": _utc_now().isoformat(),
        "data_available": False,
        "coordination_band": "UNKNOWN",
        "coordination_score": None,
        "coordination_summary": note,
        "bottlenecks": [],
        "cross_role_dependencies": [],
        "synchronization": [],
        "handoff_risks": [],
        "communication_gaps": [],
        "team_execution_flow": {
            "reports_last_7_days": 0,
            "approvals_last_7_days": 0,
            "assignments_last_7_days": 0,
            "open_coordination_dependencies": 0,
            "coordination_density": 0,
            "supervisor_responsiveness_ratio": 0,
            "workflow_step_count": 0,
            "activity_count": 0,
        },
        "coordination_attention": [],
        "worker_relevance": [
            "Full coordination analysis requires PostgreSQL and project access.",
        ],
        "false_positive_notes": [
            "Coordination signals are rule-based, not autonomous orchestration.",
            "Short pilot windows can look like misalignment when work is simply not started.",
            "Tune OPS_STALL_DAYS and OPS_APPROVAL_DELAY_DAYS with Stage 28–29 settings.",
        ],
    }


def build_project_coordination_intelligence(
    db: Session | None,
    project_id: UUID,
) -> dict[str, Any]:
    intel = build_project_operational_intelligence(db, project_id)
    stall_days = intel.get("stall_threshold_days", _stall_days())
    approval_days = intel.get("approval_delay_threshold_days", _approval_delay_days())

    if db is None or not intel.get("data_available"):
        base = _empty_coordination(
            project_id,
            "Connect PostgreSQL for cross-role coordination analysis.",
        )
        base["bottlenecks"] = _bottlenecks_from_intel(intel)
        base["worker_relevance"] = _worker_relevance_degraded(intel)
        return base

    try:
        return _build_coordination_db(db, project_id, intel, stall_days, approval_days)
    except Exception:  # noqa: BLE001
        return _empty_coordination(
            project_id,
            "Could not compute coordination intelligence (query error).",
        )


def _build_coordination_db(
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

    steps_rows = db.execute(
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

    open_blockers = db.execute(
        select(Blocker, WorkflowStep, ActivityInstance)
        .join(WorkflowStep, Blocker.workflow_step_id == WorkflowStep.id)
        .join(ActivityInstance, WorkflowStep.activity_instance_id == ActivityInstance.id)
        .where(ActivityInstance.project_id == project_id)
        .where(Blocker.status.in_(_OPEN_BLOCKER)),
    ).all()

    work_orders = list(
        db.scalars(select(WorkOrder).where(WorkOrder.project_id == project_id)).all(),
    )

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

    approvals_7d = _audit_action_count_project(project_id, "approve", days=7)
    assign_7d = _audit_action_count_project(project_id, "assign", days=7)
    conflicts_7d = _audit_conflicts_for_project(project_id, days=7)

    bottlenecks: list[dict[str, Any]] = []
    cross_role: list[dict[str, Any]] = []
    sync_signals: list[dict[str, Any]] = []
    handoffs: list[dict[str, Any]] = []
    comm_gaps: list[dict[str, Any]] = []
    attention: list[dict[str, Any]] = []

    blocked_chain = 0
    for blocker, step, act in open_blockers:
        if step.status in ("IN_PROGRESS", "INSPECTION_PENDING", "REWORK_REQUIRED"):
            blocked_chain += 1
            handoffs.append(
                _handoff(
                    "blocked_execution_chain",
                    "warning",
                    f"Step {step.code} blocked while {blocker.severity} blocker open",
                    step.id,
                    act.code,
                ),
            )

    if blocked_chain >= 2:
        bottlenecks.append(
            _signal(
                "blocked_execution_chain",
                "critical" if blocked_chain >= 4 else "warning",
                f"{blocked_chain} step(s) cannot progress due to open blockers.",
                "Blocker must be resolved before downstream handoff.",
                blocked_chain,
            ),
        )

    delayed_pending = []
    for approval, step, act in pending_approvals:
        updated = approval.updated_at
        if updated.tzinfo is None:
            updated = updated.replace(tzinfo=timezone.utc)
        if updated < approval_cutoff:
            delayed_pending.append((approval, step, act))

    if len(pending_approvals) > reports_7d and reports_7d > 0:
        cross_role.append(
            _dependency(
                "worker",
                "supervisor",
                "approval_backlog",
                "warning",
                f"{len(pending_approvals)} pending approvals vs {reports_7d} reports (7d).",
                "Field reports are outpacing supervisor sign-off.",
            ),
        )

    if delayed_pending:
        cross_role.append(
            _dependency(
                "supervisor",
                "execution",
                "delayed_approval_chain",
                "critical" if len(delayed_pending) >= 3 else "warning",
                f"{len(delayed_pending)} approval(s) exceed {approval_days}-day response window.",
                "Downstream steps wait on supervisor action.",
            ),
        )
        bottlenecks.append(
            _signal(
                "approval_coordination_delay",
                "critical" if len(delayed_pending) >= 3 else "warning",
                "Supervisor approval chain is slowing coordinated execution.",
                f"{len(delayed_pending)} overdue pending approval(s).",
                len(delayed_pending),
            ),
        )

    inactive_wos = []
    wos_without_recent_report = []
    for wo in work_orders:
        updated = wo.updated_at
        if updated.tzinfo is None:
            updated = updated.replace(tzinfo=timezone.utc)
        if wo.status in _INACTIVE_WO and updated < stall_cutoff:
            inactive_wos.append(wo)
        if wo.status in ("ASSIGNED", "IN_PROGRESS"):
            recent = db.scalar(
                select(func.count())
                .select_from(DailyReport)
                .where(DailyReport.work_order_id == wo.id)
                .where(DailyReport.report_date >= report_cutoff),
            )
            if not recent:
                wos_without_recent_report.append(wo)

    if wos_without_recent_report:
        cross_role.append(
            _dependency(
                "supervisor",
                "worker",
                "reporting_handoff",
                "warning",
                f"{len(wos_without_recent_report)} assigned work order(s) lack reports (7d).",
                "Assignment without field feedback breaks the coordination loop.",
            ),
        )
        for wo in wos_without_recent_report[:5]:
            handoffs.append(
                _handoff(
                    "incomplete_field_handoff",
                    "warning",
                    f"WO {wo.work_order_number} assigned but no report in 7 days",
                    None,
                    wo.work_order_number,
                ),
            )

    if assign_7d > reports_7d + 2 and reports_7d > 0:
        cross_role.append(
            _dependency(
                "supervisor",
                "worker",
                "assign_report_gap",
                "info",
                f"{assign_7d} assignments vs {reports_7d} reports this week.",
                "Assignments may be ahead of field confirmation.",
            ),
        )

    activity_progress: dict[str, list[Decimal]] = defaultdict(list)
    activity_step_counts: Counter[str] = Counter()
    stalled_by_activity: Counter[str] = Counter()
    for step, act in steps_rows:
        activity_progress[act.code].append(step.progress_percent)
        activity_step_counts[act.code] += 1
        updated = step.updated_at
        if updated.tzinfo is None:
            updated = updated.replace(tzinfo=timezone.utc)
        if step.status in _STALL_STEP and updated < stall_cutoff:
            stalled_by_activity[act.code] += 1

    drift_activities = []
    for code, progresses in activity_progress.items():
        if len(progresses) < 2:
            continue
        spread = float(max(progresses) - min(progresses))
        if spread >= 50:
            drift_activities.append((code, spread))

    if drift_activities:
        sync_signals.append(
            _signal(
                "execution_drift",
                "warning",
                f"{len(drift_activities)} activity area(s) show uneven step progress.",
                "Steps within the same activity diverge by 50+ points.",
                len(drift_activities),
            ),
        )

    planned_only = sum(1 for s, _ in steps_rows if s.status == "PLANNED")
    in_progress = sum(1 for s, _ in steps_rows if s.status == "IN_PROGRESS")
    if planned_only >= 5 and in_progress == 0:
        sync_signals.append(
            _signal(
                "coordination_fragmentation",
                "warning",
                "Planned work exists but no step is IN_PROGRESS.",
                "Team may be waiting on planning handoff or assignment.",
                planned_only,
            ),
        )

    isolated = [code for code, n in stalled_by_activity.items() if n >= 2]
    if isolated:
        sync_signals.append(
            _signal(
                "isolated_stalled_areas",
                "info",
                f"Stagnation clustered in: {', '.join(isolated[:3])}.",
                "Downstream areas may be starved of coordinated input.",
                len(isolated),
            ),
        )

    inspection_waiting = [
        (s, a)
        for s, a in steps_rows
        if s.status == "INSPECTION_PENDING"
    ]
    for step, act in inspection_waiting:
        has_pending = any(
            ap.workflow_step_id == step.id for ap, _, _ in pending_approvals
        )
        if has_pending:
            handoffs.append(
                _handoff(
                    "approval_handoff_pending",
                    "warning",
                    f"Step {step.code} in inspection — approval not completed",
                    step.id,
                    act.code,
                ),
            )

    rework = [(s, a) for s, a in steps_rows if s.status == "REWORK_REQUIRED"]
    if rework:
        comm_gaps.append(
            _signal(
                "rework_clarification_loop",
                "warning",
                f"{len(rework)} step(s) in REWORK_REQUIRED.",
                "Often indicates clarification or failed handoff.",
                len(rework),
            ),
        )

    stale_blockers = []
    for b, _, _ in open_blockers:
        if (date.today() - b.detected_date).days >= stall_days:
            stale_blockers.append(b)
    if stale_blockers:
        comm_gaps.append(
            _signal(
                "unresolved_blocker_communication",
                "warning",
                f"{len(stale_blockers)} blocker(s) open without resolution >={stall_days}d.",
                "No downstream movement expected until resolved.",
                len(stale_blockers),
            ),
        )

    if conflicts_7d >= 2:
        comm_gaps.append(
            _signal(
                "clarification_loop",
                "info",
                f"{conflicts_7d} concurrency conflict(s) in 7 days.",
                "May indicate overlapping edits or unclear ownership.",
                conflicts_7d,
            ),
        )

    open_deps = len(pending_approvals) + len(open_blockers) + len(inactive_wos)
    step_count = max(len(steps_rows), 1)
    density = round(open_deps / step_count, 2)
    responsiveness = round(
        approvals_7d / max(reports_7d, 1),
        2,
    )

    team_flow = {
        "reports_last_7_days": reports_7d,
        "approvals_last_7_days": approvals_7d,
        "assignments_last_7_days": assign_7d,
        "open_coordination_dependencies": open_deps,
        "coordination_density": density,
        "supervisor_responsiveness_ratio": responsiveness,
        "workflow_step_count": len(steps_rows),
        "activity_count": len(activity_progress),
    }

    score = 100
    if len(delayed_pending) >= 3:
        score -= 25
    elif delayed_pending:
        score -= 10
    if blocked_chain >= 2:
        score -= 20
    if wos_without_recent_report:
        score -= min(20, 5 * len(wos_without_recent_report))
    if drift_activities:
        score -= 10
    if stale_blockers:
        score -= min(15, 5 * len(stale_blockers))
    score = max(0, score)

    if score >= 75:
        band = "ALIGNED"
        summary = "Cross-role handoffs are within expected coordination bounds."
    elif score >= 50:
        band = "FRAGMENTED"
        summary = "Some handoffs or approvals are out of sync — review coordination attention."
    else:
        band = "STRESSED"
        summary = "Multiple coordination bottlenecks — align supervisor and field cadence."

    attention = _coordination_attention(
        handoffs,
        delayed_pending,
        open_blockers,
        wos_without_recent_report,
        bottlenecks,
    )

    worker_rel = _worker_relevance(
        wos_without_recent_report,
        pending_approvals,
        reports_7d,
        intel,
    )

    return {
        "project_id": str(project_id),
        "generated_at": now.isoformat(),
        "data_available": True,
        "coordination_band": band,
        "coordination_score": score,
        "coordination_summary": summary,
        "bottlenecks": bottlenecks,
        "cross_role_dependencies": cross_role,
        "synchronization": sync_signals,
        "handoff_risks": handoffs[:15],
        "communication_gaps": comm_gaps,
        "team_execution_flow": team_flow,
        "coordination_attention": attention,
        "worker_relevance": worker_rel,
        "false_positive_notes": [
            "Coordination intelligence does not auto-assign or auto-approve.",
            "Same-day batch approvals can look like bursts, not misalignment.",
            "Investor view summarizes band and top risks only in the UI.",
        ],
    }


def _signal(
    signal_type: str,
    severity: str,
    message: str,
    evidence: str,
    count: int,
) -> dict[str, Any]:
    return {
        "signal_type": signal_type,
        "severity": severity,
        "message": message,
        "evidence": evidence,
        "count": count,
    }


def _dependency(
    from_role: str,
    to_role: str,
    dependency_type: str,
    severity: str,
    message: str,
    evidence: str,
) -> dict[str, Any]:
    return {
        "from_role": from_role,
        "to_role": to_role,
        "dependency_type": dependency_type,
        "severity": severity,
        "message": message,
        "evidence": evidence,
    }


def _handoff(
    handoff_type: str,
    severity: str,
    message: str,
    workflow_step_id: UUID | None,
    context: str,
) -> dict[str, Any]:
    return {
        "handoff_type": handoff_type,
        "severity": severity,
        "message": message,
        "workflow_step_id": str(workflow_step_id) if workflow_step_id else None,
        "context": context,
    }


def _bottlenecks_from_intel(intel: dict[str, Any]) -> list[dict[str, Any]]:
    return list(intel.get("stagnation", []))[:3] + list(
        intel.get("approval_delays", []),
    )[:2]


def _worker_relevance_degraded(intel: dict[str, Any]) -> list[str]:
    band = intel.get("health", {}).get("band", "UNKNOWN")
    if band == "AT_RISK":
        return [
            "Project health is at risk — confirm your work orders with your supervisor.",
        ]
    return ["Submit daily reports for assigned work orders to stay aligned with the team."]


def _worker_relevance(
    wos_without_report: list,
    pending_approvals: list,
    reports_7d: int,
    intel: dict[str, Any],
) -> list[str]:
    lines: list[str] = []
    if wos_without_report:
        lines.append(
            f"You have {len(wos_without_report)} assigned work order(s) without "
            "a report in the last 7 days — submit a daily report to close the loop.",
        )
    if reports_7d > 0 and pending_approvals:
        lines.append(
            f"Your recent reports ({reports_7d} this week) are waiting on "
            f"{len(pending_approvals)} supervisor approval(s).",
        )
    if not lines:
        if intel.get("health", {}).get("band") == "GOOD":
            lines.append("Your field reporting cadence matches current team coordination.")
        else:
            lines.append(
                "No urgent coordination action on your queue — keep submitting reports on schedule.",
            )
    return lines[:3]


def _coordination_attention(
    handoffs: list,
    delayed_pending: list,
    open_blockers: list,
    wos_without_report: list,
    bottlenecks: list,
) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for h in handoffs[:5]:
        items.append(
            {
                "severity": h["severity"],
                "category": "handoff",
                "message": h["message"],
                "workflow_step_id": h.get("workflow_step_id"),
            },
        )
    for _, step, act in delayed_pending[:3]:
        items.append(
            {
                "severity": "warning",
                "category": "coordination",
                "message": f"Approval handoff delayed on {step.code} ({act.code})",
                "workflow_step_id": str(step.id),
            },
        )
    for b, step, _ in open_blockers[:3]:
        items.append(
            {
                "severity": "critical" if b.severity in ("HIGH", "CRITICAL") else "warning",
                "category": "blocker",
                "message": f"Coordination blocked: {b.title} on {step.code}",
                "workflow_step_id": str(step.id),
            },
        )
    for wo in wos_without_report[:2]:
        items.append(
            {
                "severity": "info",
                "category": "field_handoff",
                "message": f"Field handoff gap: {wo.work_order_number}",
                "workflow_step_id": None,
            },
        )
    for bn in bottlenecks[:2]:
        items.append(
            {
                "severity": bn["severity"],
                "category": "bottleneck",
                "message": bn["message"],
                "workflow_step_id": None,
            },
        )
    return items[:12]
