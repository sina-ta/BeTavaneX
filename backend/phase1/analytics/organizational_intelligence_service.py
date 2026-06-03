"""Organizational execution intelligence across projects (Stage 31) — explainable heuristics."""

from __future__ import annotations

import os
from collections import Counter
from datetime import date, datetime, timedelta, timezone
from typing import Any
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.phase1.analytics.audit_store import load_audit_records
from backend.phase1.analytics.operational_intelligence_service import (
    _approval_delay_days,
    _stall_days,
    _utc_now,
    build_project_operational_intelligence,
)
from backend.phase1.models.activity_instance import ActivityInstance
from backend.phase1.models.approval import Approval
from backend.phase1.models.blocker import Blocker
from backend.phase1.models.daily_report import DailyReport
from backend.phase1.models.project import Project
from backend.phase1.models.work_order import WorkOrder
from backend.phase1.models.workflow_step import WorkflowStep

_OPEN_BLOCKER = frozenset(
    {"OPEN", "ACKNOWLEDGED", "MITIGATION_IN_PROGRESS", "REOPENED"},
)
_PENDING_APPROVAL = frozenset({"PENDING", "UNDER_REVIEW"})
_STALL_STEP = frozenset(
    {"IN_PROGRESS", "INSPECTION_PENDING", "REWORK_REQUIRED", "PLANNED"},
)
_MAX_PROJECTS = int(os.getenv("ORG_INTEL_MAX_PROJECTS", "25"))


def _empty_org(note: str) -> dict[str, Any]:
    return {
        "generated_at": _utc_now().isoformat(),
        "data_available": False,
        "projects_analyzed": 0,
        "maturity_band": "UNKNOWN",
        "maturity_score": None,
        "maturity_summary": note,
        "maturity_components": [],
        "capacity_band": "UNKNOWN",
        "capacity_summary": note,
        "cross_project_findings": [],
        "organizational_bottlenecks": [],
        "supervisor_trends": [],
        "culture_indicators": [],
        "multi_project_coordination": [],
        "project_snapshots": [],
        "organizational_attention": [note],
        "false_positive_notes": [
            "Organizational signals aggregate accessible projects only.",
            "Supervisor trends use audit JSONL — not HR performance scores.",
            "Tune OPS_STALL_DAYS / OPS_APPROVAL_DELAY_DAYS for calendar context.",
        ],
    }


def build_organizational_intelligence(
    db: Session | None,
    accessible_project_ids: set[UUID] | None,
) -> dict[str, Any]:
    if db is None:
        return _empty_org(
            "Connect PostgreSQL for cross-project organizational intelligence.",
        )
    try:
        return _build_org_db(db, accessible_project_ids)
    except Exception:  # noqa: BLE001
        return _empty_org("Could not compute organizational intelligence (query error).")


def _build_org_db(
    db: Session,
    accessible_project_ids: set[UUID] | None,
) -> dict[str, Any]:
    now = _utc_now()
    stall_days = _stall_days()
    approval_days = _approval_delay_days()
    stall_cutoff = now - timedelta(days=stall_days)
    approval_cutoff = now - timedelta(days=approval_days)
    report_cutoff = date.today() - timedelta(days=7)
    audit_cutoff = (now - timedelta(days=7)).date().isoformat()

    projects = db.scalars(select(Project).order_by(Project.code)).all()
    if accessible_project_ids is not None:
        projects = [p for p in projects if p.id in accessible_project_ids]
    projects = projects[:_MAX_PROJECTS]

    if not projects:
        return _empty_org("No accessible projects to analyze.")

    project_ids = [p.id for p in projects]
    snapshots: list[dict[str, Any]] = []
    global_blocker_types: Counter[str] = Counter()
    total_open_blockers = 0
    total_pending_approvals = 0
    total_delayed_approvals = 0
    total_reports_7d = 0
    total_stalled = 0
    projects_with_reports = 0
    projects_with_execution = 0
    projects_at_risk = 0
    pressure_scores: list[tuple[UUID, str, str, int]] = []

    for project in projects:
        pid = project.id
        steps = db.execute(
            select(WorkflowStep, ActivityInstance)
            .join(
                ActivityInstance,
                WorkflowStep.activity_instance_id == ActivityInstance.id,
            )
            .where(ActivityInstance.project_id == pid),
        ).all()

        stalled = 0
        in_progress = 0
        for step, _ in steps:
            updated = step.updated_at
            if updated.tzinfo is None:
                updated = updated.replace(tzinfo=timezone.utc)
            if step.status == "IN_PROGRESS":
                in_progress += 1
            if step.status in _STALL_STEP and updated < stall_cutoff:
                stalled += 1
        total_stalled += stalled
        if in_progress > 0:
            projects_with_execution += 1

        pending = db.execute(
            select(func.count())
            .select_from(Approval)
            .join(WorkflowStep, Approval.workflow_step_id == WorkflowStep.id)
            .join(ActivityInstance, WorkflowStep.activity_instance_id == ActivityInstance.id)
            .where(ActivityInstance.project_id == pid)
            .where(Approval.status.in_(_PENDING_APPROVAL)),
        ).scalar() or 0

        delayed = db.execute(
            select(Approval)
            .join(WorkflowStep, Approval.workflow_step_id == WorkflowStep.id)
            .join(ActivityInstance, WorkflowStep.activity_instance_id == ActivityInstance.id)
            .where(ActivityInstance.project_id == pid)
            .where(Approval.status.in_(_PENDING_APPROVAL)),
        ).scalars().all()
        delayed_n = 0
        for approval in delayed:
            updated = approval.updated_at
            if updated.tzinfo is None:
                updated = updated.replace(tzinfo=timezone.utc)
            if updated < approval_cutoff:
                delayed_n += 1

        open_b = db.execute(
            select(Blocker, WorkflowStep, ActivityInstance)
            .join(WorkflowStep, Blocker.workflow_step_id == WorkflowStep.id)
            .join(ActivityInstance, WorkflowStep.activity_instance_id == ActivityInstance.id)
            .where(ActivityInstance.project_id == pid)
            .where(Blocker.status.in_(_OPEN_BLOCKER)),
        ).all()
        for b, _, _ in open_b:
            global_blocker_types[b.blocker_type] += 1
        total_open_blockers += len(open_b)

        reports_7d = (
            db.scalar(
                select(func.count())
                .select_from(DailyReport)
                .join(WorkOrder, DailyReport.work_order_id == WorkOrder.id)
                .where(WorkOrder.project_id == pid)
                .where(DailyReport.report_date >= report_cutoff),
            )
            or 0
        )
        total_reports_7d += reports_7d
        if reports_7d > 0:
            projects_with_reports += 1

        total_pending_approvals += pending
        total_delayed_approvals += delayed_n

        intel = build_project_operational_intelligence(db, pid)
        health_band = intel.get("health", {}).get("band", "UNKNOWN")
        if health_band == "AT_RISK":
            projects_at_risk += 1

        pressure = pending + len(open_b) + stalled
        pressure_label = (
            "high" if pressure >= 8 else "medium" if pressure >= 4 else "low"
        )
        pressure_scores.append((pid, project.code, project.name, pressure))

        snapshots.append(
            {
                "project_id": str(pid),
                "project_code": project.code,
                "project_name": project.name,
                "health_band": health_band,
                "coordination_pressure": pressure_label,
                "open_blockers": len(open_b),
                "pending_approvals": pending,
                "reports_last_7_days": reports_7d,
                "stalled_steps": stalled,
            },
        )

    n = len(projects)
    maturity_components = _maturity_components(
        n,
        projects_with_execution,
        projects_with_reports,
        total_pending_approvals,
        total_delayed_approvals,
        total_open_blockers,
        total_stalled,
        global_blocker_types,
    )
    maturity_score = (
        sum(c["score"] for c in maturity_components) // len(maturity_components)
        if maturity_components
        else None
    )
    maturity_band = _maturity_band(maturity_score)
    capacity_band, capacity_summary = _capacity_assessment(
        total_pending_approvals,
        total_open_blockers,
        total_reports_7d,
        n,
    )

    cross_project = _cross_project_findings(
        global_blocker_types,
        total_stalled,
        total_delayed_approvals,
        projects_at_risk,
        n,
        stall_days,
        approval_days,
    )
    bottlenecks = _organizational_bottlenecks(
        total_delayed_approvals,
        total_pending_approvals,
        total_open_blockers,
        total_stalled,
        n,
    )
    supervisor_trends = _supervisor_trends(audit_cutoff, total_pending_approvals)
    culture = _culture_indicators(
        total_delayed_approvals,
        total_open_blockers,
        global_blocker_types,
        total_reports_7d,
        n,
    )
    multi_project = _multi_project_signals(pressure_scores, projects_at_risk, n)
    attention = _organizational_attention(
        maturity_band,
        capacity_band,
        projects_at_risk,
        total_delayed_approvals,
        cross_project,
        bottlenecks,
    )

    return {
        "generated_at": now.isoformat(),
        "data_available": True,
        "projects_analyzed": n,
        "maturity_band": maturity_band,
        "maturity_score": maturity_score,
        "maturity_summary": _maturity_summary(maturity_band, maturity_score, n),
        "maturity_components": maturity_components,
        "capacity_band": capacity_band,
        "capacity_summary": capacity_summary,
        "cross_project_findings": cross_project,
        "organizational_bottlenecks": bottlenecks,
        "supervisor_trends": supervisor_trends,
        "culture_indicators": culture,
        "multi_project_coordination": multi_project,
        "project_snapshots": sorted(
            snapshots,
            key=lambda s: (
                s["coordination_pressure"] == "high",
                s["pending_approvals"] + s["open_blockers"],
            ),
            reverse=True,
        )[:12],
        "organizational_attention": attention,
        "false_positive_notes": [
            "Analysis capped at ORG_INTEL_MAX_PROJECTS (default 25).",
            "Supervisor observations describe audit activity share, not HR ratings.",
            "Single-pilot testers can mimic organizational concentration.",
            "Compare per-project health with Stage 28 before org-wide escalation.",
        ],
    }


def _maturity_components(
    project_count: int,
    with_execution: int,
    with_reports: int,
    pending: int,
    delayed: int,
    open_blockers: int,
    stalled: int,
    blocker_types: Counter[str],
) -> list[dict[str, Any]]:
    if project_count == 0:
        return []

    continuity = int(100 * with_execution / project_count)
    reporting = int(100 * with_reports / project_count) if project_count else 0
    approval_disc = 100
    if pending > 0:
        approval_disc = int(100 * (pending - delayed) / pending)
    blocker_resp = 100
    if open_blockers > 0:
        long_types = sum(1 for _, c in blocker_types.items() if c >= 2)
        blocker_resp = max(40, 100 - min(40, long_types * 15 + stalled))
    coordination = max(
        0,
        100 - min(50, (pending + open_blockers) // max(1, project_count) * 8),
    )
    recovery = max(0, 100 - min(30, stalled // max(1, project_count) * 10))

    return [
        {
            "factor": "workflow_continuity",
            "score": continuity,
            "detail": f"{with_execution}/{project_count} projects have IN_PROGRESS steps.",
        },
        {
            "factor": "reporting_reliability",
            "score": reporting,
            "detail": f"{with_reports}/{project_count} projects reported in the last 7 days.",
        },
        {
            "factor": "approval_discipline",
            "score": approval_disc,
            "detail": f"{delayed} overdue of {pending} pending approvals org-wide.",
        },
        {
            "factor": "blocker_responsiveness",
            "score": blocker_resp,
            "detail": f"{open_blockers} open blockers; recurring types: {len(blocker_types)}.",
        },
        {
            "factor": "coordination_consistency",
            "score": coordination,
            "detail": "Derived from pending approvals + open blockers per project average.",
        },
        {
            "factor": "operational_recovery",
            "score": recovery,
            "detail": f"{stalled} stalled steps aggregated across projects.",
        },
    ]


def _maturity_band(score: int | None) -> str:
    if score is None:
        return "UNKNOWN"
    if score >= 75:
        return "ESTABLISHED"
    if score >= 55:
        return "DEVELOPING"
    if score >= 35:
        return "EMERGING"
    return "STRAINED"


def _maturity_summary(band: str, score: int | None, n: int) -> str:
    if band == "ESTABLISHED":
        return f"Execution maturity ESTABLISHED ({score}/100) across {n} project(s)."
    if band == "DEVELOPING":
        return f"Execution maturity DEVELOPING ({score}/100) — some coordination gaps remain."
    if band == "EMERGING":
        return f"Execution maturity EMERGING ({score}/100) — strengthen reporting and approvals."
    if band == "STRAINED":
        return f"Execution maturity STRAINED ({score}/100) — org-wide execution review recommended."
    return "Maturity unknown — insufficient project data."


def _capacity_assessment(
    pending: int,
    blockers: int,
    reports: int,
    projects: int,
) -> tuple[str, str]:
    load = pending + blockers
    throughput = reports + 1
    ratio = load / throughput
    per_project = load / max(1, projects)
    if ratio >= 3 or per_project >= 10:
        return (
            "SATURATED",
            "Operational load (approvals + blockers) exceeds recent reporting throughput.",
        )
    if ratio >= 1.5 or per_project >= 5:
        return (
            "PRESSURED",
            "Execution dependencies are accumulating — monitor supervisor capacity.",
        )
    return (
        "BALANCED",
        "Reporting throughput and open dependencies are within pilot-scale balance.",
    )


def _cross_project_findings(
    blocker_types: Counter[str],
    stalled: int,
    delayed: int,
    at_risk: int,
    projects: int,
    stall_days: int,
    approval_days: int,
) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    if blocker_types:
        top = blocker_types.most_common(3)
        findings.append(
            {
                "signal_type": "recurring_blocker_types",
                "severity": "warning" if top[0][1] >= 3 else "info",
                "message": "Organization-wide blocker pattern: "
                + ", ".join(f"{k} ({v})" for k, v in top),
                "evidence": "Aggregated open blockers across accessible projects.",
                "count": sum(blocker_types.values()),
            },
        )
    if stalled >= projects and projects > 0:
        findings.append(
            {
                "signal_type": "workflow_slowdown_pattern",
                "severity": "warning",
                "message": f"{stalled} stalled steps — slowdown appears in multiple workflows.",
                "evidence": f"Steps inactive >{stall_days} days.",
                "count": stalled,
            },
        )
    if delayed >= 3:
        findings.append(
            {
                "signal_type": "approval_bottleneck_pattern",
                "severity": "critical" if delayed >= 5 else "warning",
                "message": f"{delayed} overdue approvals across {projects} project(s).",
                "evidence": f"Threshold {approval_days} days (Stage 28/29).",
                "count": delayed,
            },
        )
    if at_risk >= 2:
        findings.append(
            {
                "signal_type": "execution_drift",
                "severity": "warning",
                "message": f"{at_risk} project(s) at AT_RISK health band (Stage 28).",
                "evidence": "Repeated operational instability signal.",
                "count": at_risk,
            },
        )
    return findings


def _organizational_bottlenecks(
    delayed: int,
    pending: int,
    blockers: int,
    stalled: int,
    projects: int,
) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    if delayed >= 2:
        items.append(
            {
                "signal_type": "chronic_approval_congestion",
                "severity": "critical",
                "message": "Chronic approval congestion detected organization-wide.",
                "evidence": f"{delayed} overdue of {pending} pending.",
                "count": delayed,
            },
        )
    if blockers >= 5:
        items.append(
            {
                "signal_type": "blocker_choke_point",
                "severity": "warning",
                "message": f"{blockers} open blockers create execution choke points.",
                "evidence": "Multi-project blocker accumulation.",
                "count": blockers,
            },
        )
    if stalled >= projects * 2 and projects > 0:
        items.append(
            {
                "signal_type": "coordination_failure_pattern",
                "severity": "warning",
                "message": "Persistent coordination failures — stalled steps exceed project count.",
                "evidence": "Cross-project stagnation heuristic.",
                "count": stalled,
            },
        )
    if pending >= 10:
        items.append(
            {
                "signal_type": "execution_capacity_imbalance",
                "severity": "warning",
                "message": f"{pending} pending approvals — governance load exceeds field cadence.",
                "evidence": "Approval queue depth org-wide.",
                "count": pending,
            },
        )
    return items


def _supervisor_trends(
    audit_cutoff: str,
    pending_org: int,
) -> list[dict[str, Any]]:
    by_user: Counter[str] = Counter()
    by_role: dict[str, str] = {}
    approve: Counter[str] = Counter()
    assign: Counter[str] = Counter()

    for record in load_audit_records():
        occurred = (record.get("occurred_at") or "")[:10]
        if occurred < audit_cutoff:
            continue
        role = record.get("role", "")
        if role not in ("admin", "supervisor"):
            continue
        user = record.get("username", "")
        if not user:
            continue
        by_user[user] += 1
        by_role[user] = role
        action = (record.get("action") or "").lower()
        if "approve" in action:
            approve[user] += 1
        if "assign" in action:
            assign[user] += 1

    total = sum(by_user.values()) or 1
    trends: list[dict[str, Any]] = []
    for user, count in by_user.most_common(8):
        share = count / total
        a = approve[user]
        g = assign[user]
        concentration = share >= 0.6 and count >= 4
        if a >= 5 and pending_org >= a * 2:
            obs = (
                f"High approval activity ({a}/7d) while org pending queue is {pending_org} — "
                "may indicate overload or catch-up batch."
            )
        elif a >= 3 and g >= 2:
            obs = f"Balanced governance ({a} approvals, {g} assignments in 7d)."
        elif a >= 3:
            obs = f"Approval-focused week ({a} approvals) — monitor field reporting match."
        elif g >= 3:
            obs = f"Assignment-focused week ({g} assignments) — confirm field follow-through."
        else:
            obs = f"Light operational audit activity ({count} actions in 7d)."
        if concentration:
            obs += " Organizational dependency concentration on this account."
        trends.append(
            {
                "username": user,
                "role": by_role.get(user, "supervisor"),
                "approvals_7d": a,
                "assignments_7d": g,
                "audit_actions_7d": count,
                "observation": obs,
                "concentration_risk": concentration,
            },
        )
    return trends


def _culture_indicators(
    delayed: int,
    open_blockers: int,
    blocker_types: Counter[str],
    reports_7d: int,
    projects: int,
) -> list[dict[str, Any]]:
    culture: list[dict[str, Any]] = []
    if delayed >= 2:
        culture.append(
            {
                "signal_type": "delayed_approvals_habit",
                "severity": "warning",
                "message": "Delayed approvals recur across projects — approval discipline gap.",
                "evidence": "Operational habit, not individual psychology.",
                "count": delayed,
            },
        )
    if open_blockers >= 4 and len(blocker_types) <= 2:
        culture.append(
            {
                "signal_type": "ignored_blockers_pattern",
                "severity": "warning",
                "message": "Few blocker categories stay open org-wide — possible resolution avoidance.",
                "evidence": f"{open_blockers} open; types: {list(blocker_types.keys())[:3]}",
                "count": open_blockers,
            },
        )
    if reports_7d < projects and projects >= 2:
        culture.append(
            {
                "signal_type": "reporting_inconsistency",
                "severity": "info",
                "message": "Reporting cadence inconsistent — not all projects filed in 7 days.",
                "evidence": f"{reports_7d} reports vs {projects} projects.",
                "count": reports_7d,
            },
        )
    if delayed >= 1 and reports_7d >= 5:
        culture.append(
            {
                "signal_type": "reactive_execution",
                "severity": "info",
                "message": "Field reports active while approvals lag — reactive governance pattern.",
                "evidence": "Reports without matching approval throughput.",
                "count": reports_7d,
            },
        )
    if not culture:
        culture.append(
            {
                "signal_type": "discipline_stable",
                "severity": "info",
                "message": "No major operational culture risks at current thresholds.",
                "evidence": "Heuristic scan across projects.",
                "count": 0,
            },
        )
    return culture


def _multi_project_signals(
    pressure_scores: list[tuple[UUID, str, str, int]],
    at_risk: int,
    projects: int,
) -> list[dict[str, Any]]:
    signals: list[dict[str, Any]] = []
    high = [p for p in pressure_scores if p[3] >= 8]
    if len(high) >= 2:
        names = ", ".join(p[1] for p in high[:4])
        signals.append(
            {
                "signal_type": "competing_project_attention",
                "severity": "warning",
                "message": f"{len(high)} project(s) compete for attention: {names}.",
                "evidence": "High coordination pressure score (approvals+blockers+stalled).",
                "count": len(high),
            },
        )
    if at_risk >= 1 and projects >= 2:
        signals.append(
            {
                "signal_type": "coordination_hotspot",
                "severity": "warning" if at_risk >= 2 else "info",
                "message": f"{at_risk} project(s) show deteriorating execution health.",
                "evidence": "Stage 28 AT_RISK band count.",
                "count": at_risk,
            },
        )
    overloaded = sum(1 for _, _, _, score in pressure_scores if score >= 4)
    if overloaded >= max(2, projects // 2):
        signals.append(
            {
                "signal_type": "operational_imbalance",
                "severity": "info",
                "message": "Operational load uneven — multiple projects above medium pressure.",
                "evidence": "Per-project pressure heuristic.",
                "count": overloaded,
            },
        )
    return signals


def _organizational_attention(
    maturity_band: str,
    capacity_band: str,
    at_risk: int,
    delayed: int,
    cross: list[dict[str, Any]],
    bottlenecks: list[dict[str, Any]],
) -> list[str]:
    lines: list[str] = []
    if maturity_band == "STRAINED":
        lines.append(
            "Organizational execution maturity STRAINED — executive/supervisor review recommended.",
        )
    if capacity_band == "SATURATED":
        lines.append(
            "Execution capacity SATURATED — defer new assignments until queues clear.",
        )
    elif capacity_band == "PRESSURED":
        lines.append("Execution capacity PRESSURED — prioritize bottleneck clearance.")
    if at_risk >= 2:
        lines.append(f"{at_risk} projects at AT_RISK — align Stage 28 project reviews.")
    if delayed >= 3:
        lines.append(
            f"{delayed} overdue approvals organization-wide — escalation before new work.",
        )
    for item in bottlenecks[:2]:
        lines.append(item["message"])
    for item in cross[:2]:
        if item["severity"] in ("critical", "warning"):
            lines.append(item["message"])
    if not lines:
        lines.append(
            "Organizational execution within expected pilot bounds — continue monitoring.",
        )
    return lines[:8]
