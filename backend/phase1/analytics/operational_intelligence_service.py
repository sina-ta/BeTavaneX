"""Explainable operational intelligence from runtime DB + pilot JSONL (Stage 28)."""

from __future__ import annotations

import os
from collections import Counter
from datetime import date, datetime, timedelta, timezone
from typing import Any
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.phase1.analytics.audit_store import load_audit_records
from backend.phase1.analytics.usage_store import load_usage_events
from backend.phase1.models.activity_instance import ActivityInstance
from backend.phase1.models.approval import Approval
from backend.phase1.models.blocker import Blocker
from backend.phase1.models.daily_report import DailyReport
from backend.phase1.models.work_order import WorkOrder
from backend.phase1.models.workflow_step import WorkflowStep

_OPEN_BLOCKER = frozenset(
    {"OPEN", "ACKNOWLEDGED", "MITIGATION_IN_PROGRESS", "REOPENED"},
)
_STALL_STEP_STATUSES = frozenset(
    {"IN_PROGRESS", "INSPECTION_PENDING", "REWORK_REQUIRED", "PLANNED"},
)
_PENDING_APPROVAL = frozenset({"PENDING", "UNDER_REVIEW"})
_INACTIVE_WO = frozenset({"CREATED", "ASSIGNED"})


def _stall_days() -> int:
    return int(os.getenv("OPS_STALL_DAYS", "7"))


def _approval_delay_days() -> int:
    return int(os.getenv("OPS_APPROVAL_DELAY_DAYS", "5"))


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def build_project_operational_intelligence(
    db: Session | None,
    project_id: UUID,
) -> dict[str, Any]:
    stall_days = _stall_days()
    approval_days = _approval_delay_days()
    now = _utc_now()
    stall_cutoff = now - timedelta(days=stall_days)
    approval_cutoff = now - timedelta(days=approval_days)
    report_cutoff = date.today() - timedelta(days=7)

    base: dict[str, Any] = {
        "project_id": str(project_id),
        "generated_at": now.isoformat(),
        "data_available": False,
        "stall_threshold_days": stall_days,
        "approval_delay_threshold_days": approval_days,
        "health": {
            "score": None,
            "band": "UNKNOWN",
            "components": [],
            "summary": "Runtime database unavailable — intelligence requires PostgreSQL.",
        },
        "stagnation": [],
        "approval_delays": [],
        "blocker_trends": [],
        "anomalies": [],
        "attention_needed": [],
        "predictions": [],
        "false_positive_notes": [
            "Heuristics use fixed day thresholds; tune OPS_STALL_DAYS and "
            "OPS_APPROVAL_DELAY_DAYS for your pilot calendar.",
            "Low data volume can trigger planning-traffic hints from Stage 27 overlap.",
        ],
    }

    if db is None:
        base["anomalies"].extend(_jsonl_anomalies(project_id, now))
        return base

    try:
        return _build_with_db(
            db,
            project_id,
            base,
            stall_cutoff,
            approval_cutoff,
            report_cutoff,
            stall_days,
            approval_days,
            now,
        )
    except Exception:  # noqa: BLE001
        base["health"]["summary"] = "Could not compute intelligence (query error)."
        return base


def _build_with_db(
    db: Session,
    project_id: UUID,
    base: dict[str, Any],
    stall_cutoff: datetime,
    approval_cutoff: datetime,
    report_cutoff: date,
    stall_days: int,
    approval_days: int,
    now: datetime,
) -> dict[str, Any]:
    base["data_available"] = True

    steps = db.execute(
        select(WorkflowStep, ActivityInstance)
        .join(
            ActivityInstance,
            WorkflowStep.activity_instance_id == ActivityInstance.id,
        )
        .where(ActivityInstance.project_id == project_id),
    ).all()

    stalled_steps = []
    for step, act in steps:
        updated = step.updated_at
        if updated.tzinfo is None:
            updated = updated.replace(tzinfo=timezone.utc)
        if step.status in _STALL_STEP_STATUSES and updated < stall_cutoff:
            stalled_steps.append((step, act))

    rework_steps = [step for step, _ in steps if step.status == "REWORK_REQUIRED"]

    pending_approvals = db.execute(
        select(Approval, WorkflowStep, ActivityInstance)
        .join(WorkflowStep, Approval.workflow_step_id == WorkflowStep.id)
        .join(ActivityInstance, WorkflowStep.activity_instance_id == ActivityInstance.id)
        .where(ActivityInstance.project_id == project_id)
        .where(Approval.status.in_(_PENDING_APPROVAL)),
    ).all()

    delayed_approvals = []
    for approval, step, act in pending_approvals:
        updated = approval.updated_at
        if updated.tzinfo is None:
            updated = updated.replace(tzinfo=timezone.utc)
        if updated < approval_cutoff:
            delayed_approvals.append((approval, step, act))

    blockers = db.execute(
        select(Blocker, WorkflowStep, ActivityInstance)
        .join(WorkflowStep, Blocker.workflow_step_id == WorkflowStep.id)
        .join(ActivityInstance, WorkflowStep.activity_instance_id == ActivityInstance.id)
        .where(ActivityInstance.project_id == project_id),
    ).all()

    open_blockers = [
        (b, s, a) for b, s, a in blockers if b.status in _OPEN_BLOCKER
    ]
    critical_open = [
        (b, s, a)
        for b, s, a in open_blockers
        if b.severity in ("HIGH", "CRITICAL")
    ]
    long_lived = []
    for b, s, a in open_blockers:
        age_days = (date.today() - b.detected_date).days
        if age_days >= stall_days:
            long_lived.append((b, s, a, age_days))

    blocker_by_type: Counter[str] = Counter(b.blocker_type for b, _, _ in open_blockers)

    work_orders = db.scalars(
        select(WorkOrder).where(WorkOrder.project_id == project_id),
    ).all()

    inactive_wos = []
    for wo in work_orders:
        updated = wo.updated_at
        if updated.tzinfo is None:
            updated = updated.replace(tzinfo=timezone.utc)
        if wo.status in _INACTIVE_WO and updated < stall_cutoff:
            inactive_wos.append(wo)

    reports_7d = db.scalar(
        select(func.count())
        .select_from(DailyReport)
        .join(WorkOrder, DailyReport.work_order_id == WorkOrder.id)
        .where(WorkOrder.project_id == project_id)
        .where(DailyReport.report_date >= report_cutoff),
    ) or 0

    conflicts_7d = _audit_conflicts_for_project(project_id, days=7)

    stagnation: list[dict[str, Any]] = []
    if stalled_steps:
        stagnation.append(
            {
                "signal_type": "stalled_workflow_steps",
                "severity": "warning",
                "message": f"{len(stalled_steps)} workflow step(s) inactive for >{stall_days} days.",
                "evidence": f"updated_at before {stall_cutoff.date().isoformat()}",
                "count": len(stalled_steps),
            },
        )
    if rework_steps:
        stagnation.append(
            {
                "signal_type": "rework_required_steps",
                "severity": "warning",
                "message": f"{len(rework_steps)} step(s) in REWORK_REQUIRED.",
                "evidence": "Status indicates reopened execution path.",
                "count": len(rework_steps),
            },
        )
    if inactive_wos:
        stagnation.append(
            {
                "signal_type": "inactive_work_orders",
                "severity": "info",
                "message": f"{len(inactive_wos)} work order(s) stuck in CREATED/ASSIGNED.",
                "evidence": f"No status movement since {stall_cutoff.date().isoformat()}",
                "count": len(inactive_wos),
            },
        )

    approval_delays: list[dict[str, Any]] = []
    if delayed_approvals:
        approval_delays.append(
            {
                "signal_type": "delayed_pending_approvals",
                "severity": "critical" if len(delayed_approvals) >= 3 else "warning",
                "message": f"{len(delayed_approvals)} approval(s) pending >{approval_days} days.",
                "evidence": "Supervisor response delay vs threshold.",
                "count": len(delayed_approvals),
            },
        )
    if len(pending_approvals) > reports_7d and reports_7d > 0:
        approval_delays.append(
            {
                "signal_type": "approval_backlog_vs_reports",
                "severity": "warning",
                "message": (
                    f"Pending approvals ({len(pending_approvals)}) exceed "
                    f"reports in last 7 days ({reports_7d})."
                ),
                "evidence": "Operational completion bottleneck.",
                "count": len(pending_approvals),
            },
        )

    blocker_trends: list[dict[str, Any]] = []
    if open_blockers:
        top_types = ", ".join(f"{k}({v})" for k, v in blocker_by_type.most_common(3))
        blocker_trends.append(
            {
                "signal_type": "open_blockers",
                "severity": "critical" if critical_open else "warning",
                "message": f"{len(open_blockers)} open blocker(s). Types: {top_types or 'n/a'}.",
                "evidence": "Statuses in OPEN/ACKNOWLEDGED/MITIGATION/REOPENED.",
                "count": len(open_blockers),
            },
        )
    if long_lived:
        blocker_trends.append(
            {
                "signal_type": "long_lived_blockers",
                "severity": "warning",
                "message": f"{len(long_lived)} blocker(s) open >={stall_days} days.",
                "evidence": "detected_date age heuristic.",
                "count": len(long_lived),
            },
        )

    anomalies = _jsonl_anomalies(project_id, now)
    if conflicts_7d >= 2:
        anomalies.append(
            {
                "signal_type": "concurrency_spike",
                "severity": "warning",
                "message": f"{conflicts_7d} optimistic conflict(s) in last 7 days.",
                "evidence": "operational_audit.jsonl conflict category.",
                "count": conflicts_7d,
            },
        )
    report_audits_today = _audit_action_count_project(
        project_id,
        "submit",
        days=1,
    )
    if report_audits_today >= 5:
        anomalies.append(
            {
                "signal_type": "duplicate_reporting_spike",
                "severity": "info",
                "message": f"{report_audits_today} report submission audit(s) today.",
                "evidence": "May indicate retries after 409 or batch entry.",
                "count": report_audits_today,
            },
        )
    planned_count = sum(1 for s, _ in steps if s.status == "PLANNED")
    in_progress_count = sum(1 for s, _ in steps if s.status == "IN_PROGRESS")
    if planned_count >= 5 and in_progress_count == 0:
        anomalies.append(
            {
                "signal_type": "workflow_starvation",
                "severity": "warning",
                "message": f"{planned_count} PLANNED steps with zero IN_PROGRESS.",
                "evidence": "Execution not started on planned work.",
                "count": planned_count,
            },
        )

    components: list[dict[str, Any]] = []
    score = 100
    if critical_open:
        impact = min(30, 10 * len(critical_open))
        score -= impact
        components.append(
            {
                "factor": "critical_blockers",
                "impact": impact,
                "detail": f"{len(critical_open)} HIGH/CRITICAL open blocker(s).",
            },
        )
    if stalled_steps:
        impact = min(25, 5 * len(stalled_steps))
        score -= impact
        components.append(
            {
                "factor": "stalled_steps",
                "impact": impact,
                "detail": f"{len(stalled_steps)} step(s) past inactivity threshold.",
            },
        )
    if delayed_approvals:
        impact = min(20, 5 * len(delayed_approvals))
        score -= impact
        components.append(
            {
                "factor": "approval_delays",
                "impact": impact,
                "detail": f"{len(delayed_approvals)} approval(s) overdue.",
            },
        )
    if inactive_wos:
        impact = min(15, 5 * len(inactive_wos))
        score -= impact
        components.append(
            {
                "factor": "inactive_work_orders",
                "impact": impact,
                "detail": f"{len(inactive_wos)} unmoved work order(s).",
            },
        )
    if reports_7d == 0 and len(work_orders) > 0:
        impact = 10
        score -= impact
        components.append(
            {
                "factor": "reporting_gap",
                "impact": impact,
                "detail": "No daily reports in the last 7 days despite work orders.",
            },
        )
    score = max(0, score)
    if score >= 75:
        band = "GOOD"
        summary = "Operational rhythm within expected pilot bounds."
    elif score >= 50:
        band = "ATTENTION"
        summary = "Several execution signals need supervisor review."
    else:
        band = "AT_RISK"
        summary = "Multiple stagnation or blocker signals — prioritize field review."

    attention = _build_attention(
        stalled_steps,
        delayed_approvals,
        critical_open,
        inactive_wos,
    )
    predictions = _build_predictions(
        stalled_steps,
        delayed_approvals,
        open_blockers,
        pending_approvals,
        reports_7d,
        approval_days,
    )

    base.update(
        {
            "health": {
                "score": score,
                "band": band,
                "components": components,
                "summary": summary,
            },
            "stagnation": stagnation,
            "approval_delays": approval_delays,
            "blocker_trends": blocker_trends,
            "anomalies": anomalies,
            "attention_needed": attention,
            "predictions": predictions,
        },
    )
    return base


def _build_attention(
    stalled_steps: list,
    delayed_approvals: list,
    critical_open: list,
    inactive_wos: list,
) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for b, step, act in critical_open[:5]:
        items.append(
            {
                "severity": "critical",
                "category": "blocker",
                "message": f"Blocker ({b.severity}): {b.title} on step {step.code}",
                "resource_type": "blocker",
                "resource_id": str(b.id),
                "workflow_step_id": str(step.id),
            },
        )
    for approval, step, act in delayed_approvals[:5]:
        items.append(
            {
                "severity": "warning",
                "category": "approval",
                "message": f"Approval pending on {step.code} — {act.code}",
                "resource_type": "approval",
                "resource_id": str(approval.id),
                "workflow_step_id": str(step.id),
            },
        )
    for step, act in stalled_steps[:5]:
        items.append(
            {
                "severity": "warning",
                "category": "stagnation",
                "message": f"Step {step.code} stalled ({step.status}) in {act.name}",
                "resource_type": "workflow_step",
                "resource_id": str(step.id),
                "workflow_step_id": str(step.id),
            },
        )
    for wo in inactive_wos[:3]:
        items.append(
            {
                "severity": "info",
                "category": "work_order",
                "message": f"Work order {wo.work_order_number} inactive ({wo.status})",
                "resource_type": "work_order",
                "resource_id": str(wo.id),
                "workflow_step_id": None,
            },
        )
    return items


def _build_predictions(
    stalled_steps: list,
    delayed_approvals: list,
    open_blockers: list,
    pending_approvals: list,
    reports_7d: int,
    approval_days: int,
) -> list[dict[str, Any]]:
    preds: list[dict[str, Any]] = []
    if delayed_approvals:
        preds.append(
            {
                "forecast": "likely_stalled_approval",
                "confidence": "high",
                "reason": f"{len(delayed_approvals)} approval(s) already exceed {approval_days}-day threshold.",
                "workflow_step_id": str(delayed_approvals[0][1].id),
            },
        )
    elif len(pending_approvals) > reports_7d and reports_7d >= 2:
        preds.append(
            {
                "forecast": "approval_backlog_risk",
                "confidence": "medium",
                "reason": "Pending approvals accumulating faster than recent reports.",
                "workflow_step_id": str(pending_approvals[0][1].id)
                if pending_approvals
                else None,
            },
        )
    if stalled_steps and open_blockers:
        step_id = stalled_steps[0][0].id
        preds.append(
            {
                "forecast": "likely_delayed_workflow",
                "confidence": "medium",
                "reason": "Inactive steps coexist with open blockers.",
                "workflow_step_id": str(step_id),
            },
        )
    if len(pending_approvals) >= 5 and reports_7d < 3:
        preds.append(
            {
                "forecast": "operational_backlog_risk",
                "confidence": "low",
                "reason": "High pending approval count with low recent reporting.",
                "workflow_step_id": None,
            },
        )
    return preds


def _project_id_match(record: dict[str, Any], project_id: UUID) -> bool:
    pid = record.get("project_id")
    return pid is not None and str(pid) == str(project_id)


def _audit_conflicts_for_project(project_id: UUID, *, days: int) -> int:
    cutoff = _utc_now() - timedelta(days=days)
    count = 0
    for record in load_audit_records():
        if not _project_id_match(record, project_id):
            continue
        if record.get("mutation_category") != "conflict":
            continue
        occurred = record.get("occurred_at", "")
        if occurred and occurred[:10] >= cutoff.date().isoformat():
            count += 1
    return count


def _audit_action_count_project(
    project_id: UUID,
    action_substr: str,
    *,
    days: int,
) -> int:
    cutoff = (_utc_now() - timedelta(days=days)).date().isoformat()
    count = 0
    for record in load_audit_records():
        if not _project_id_match(record, project_id):
            continue
        action = record.get("action", "")
        if action_substr in action.lower():
            if (record.get("occurred_at") or "")[:10] >= cutoff:
                count += 1
    return count


def _jsonl_anomalies(project_id: UUID, now: datetime) -> list[dict[str, Any]]:
    anomalies: list[dict[str, Any]] = []
    usage = [
        e
        for e in load_usage_events()
        if str(e.get("project_id") or "") == str(project_id)
    ]
    overview = sum(
        1
        for e in usage
        if "/dashboard/overview" in e.get("page_path", "")
    )
    mutations = [
        r
        for r in load_audit_records()
        if _project_id_match(r, project_id)
        and r.get("mutation_category") != "query"
    ]
    if len(mutations) >= 5 and overview == 0:
        anomalies.append(
            {
                "signal_type": "inactive_dashboard",
                "severity": "info",
                "message": "Operational mutations without overview page views.",
                "evidence": "Usage JSONL vs audit JSONL for this project.",
                "count": len(mutations),
            },
        )
    approve_burst = sum(
        1
        for r in mutations
        if "approve" in r.get("action", "").lower()
        and (r.get("occurred_at") or "")[:10] == now.date().isoformat()
    )
    if approve_burst >= 4:
        anomalies.append(
            {
                "signal_type": "approval_burst",
                "severity": "info",
                "message": f"{approve_burst} approval audit(s) today — possible catch-up batch.",
                "evidence": "Same-day approval spike.",
                "count": approve_burst,
            },
        )
    return anomalies
