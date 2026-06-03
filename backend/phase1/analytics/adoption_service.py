"""Aggregate usage JSONL + audit JSONL + optional DB counters for pilot adoption."""

from __future__ import annotations

from collections import Counter, defaultdict
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.phase1.analytics.audit_store import load_audit_records
from backend.phase1.analytics.usage_store import load_usage_events
from backend.phase1.models.approval import Approval
from backend.phase1.models.daily_report import DailyReport
from backend.phase1.models.project import Project
from backend.phase1.models.work_order import WorkOrder
from backend.phase1.models.workflow_step import WorkflowStep


def _date_key(iso_ts: str) -> str:
    return iso_ts[:10] if iso_ts else "unknown"


def _normalize_page(path: str) -> str:
    if not path:
        return "/"
    base = path.split("?")[0].rstrip("/") or "/"
    if "/activity-instances/" in base:
        return "/dashboard/activity-instances/:id"
    return base


def build_adoption_summary(db: Session | None = None) -> dict[str, Any]:
    usage = load_usage_events()
    audits = load_audit_records()

    users_usage: set[str] = set()
    users_audit: set[str] = set()
    role_usage: Counter[str] = Counter()
    role_audit: Counter[str] = Counter()
    page_views: Counter[str] = Counter()
    events_by_type: Counter[str] = Counter()
    actions: Counter[str] = Counter()
    mutations_by_role: Counter[str] = Counter()
    user_active_days: defaultdict[str, set[str]] = defaultdict(set)
    session_pages: defaultdict[str, list[str]] = defaultdict(list)

    for event in usage:
        user = event.get("username", "")
        role = event.get("role", "unknown")
        if user:
            users_usage.add(user)
            role_usage[role] += 1
            user_active_days[user].add(_date_key(event.get("recorded_at", "")))
        page = _normalize_page(event.get("page_path", ""))
        page_views[page] += 1
        events_by_type[event.get("event_type", "page_view")] += 1
        sid = event.get("session_id")
        if sid:
            session_pages[sid].append(page)

    for record in audits:
        user = record.get("username", "")
        role = record.get("role", "unknown")
        if user:
            users_audit.add(user)
            role_audit[role] += 1
            user_active_days[user].add(_date_key(record.get("occurred_at", "")))
        action = record.get("action", "unknown")
        actions[action] += 1
        if record.get("mutation_category") != "query":
            mutations_by_role[role] += 1

    backtrack_sessions = 0
    for _sid, pages in session_pages.items():
        for index in range(2, len(pages)):
            if pages[index] == pages[index - 2] and pages[index] != pages[index - 1]:
                backtrack_sessions += 1
                break

    retention_scores = []
    for user, days in user_active_days.items():
        retention_scores.append(
            {"username": user, "active_days": len(days), "dates": sorted(days)},
        )
    retention_scores.sort(key=lambda row: row["active_days"], reverse=True)

    low_engagement_pages = [
        path
        for path, count in sorted(page_views.items(), key=lambda item: item[1])
        if count <= 2 and path.startswith("/dashboard")
    ][:8]

    db_snapshot: dict[str, int] = {}
    if db is not None:
        try:
            db_snapshot = {
                "projects_total": db.scalar(select(func.count()).select_from(Project)) or 0,
                "workflow_steps_total": db.scalar(
                    select(func.count()).select_from(WorkflowStep),
                )
                or 0,
                "work_orders_total": db.scalar(select(func.count()).select_from(WorkOrder))
                or 0,
                "daily_reports_total": db.scalar(
                    select(func.count()).select_from(DailyReport),
                )
                or 0,
                "approvals_total": db.scalar(select(func.count()).select_from(Approval))
                or 0,
            }
        except Exception:  # noqa: BLE001 — optional DB snapshot
            db_snapshot = {}

    report_actions = sum(
        count for action, count in actions.items() if "report" in action.lower()
    )
    approve_actions = sum(
        count for action, count in actions.items() if "approve" in action.lower()
    )
    assign_actions = sum(
        count for action, count in actions.items() if "assign" in action.lower()
    )

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "usage": {
            "event_count": len(usage),
            "distinct_users": len(users_usage | users_audit),
            "distinct_users_usage_only": len(users_usage),
            "by_role_events": dict(role_usage),
            "page_views": dict(page_views.most_common(20)),
            "least_used_dashboard_paths": low_engagement_pages,
            "event_types": dict(events_by_type),
            "navigation_backtrack_sessions": backtrack_sessions,
        },
        "mutations": {
            "audit_record_count": len(audits),
            "by_action": dict(actions.most_common(30)),
            "by_role": dict(mutations_by_role),
            "daily_report_actions": report_actions,
            "approval_actions": approve_actions,
            "assign_actions": assign_actions,
        },
        "retention": {
            "user_active_days": retention_scores,
            "users_with_multi_day_activity": sum(
                1 for row in retention_scores if row["active_days"] >= 2
            ),
        },
        "db_snapshot": db_snapshot,
        "bottleneck_hints": _bottleneck_hints(
            actions,
            page_views,
            approve_actions,
            report_actions,
        ),
    }


def _bottleneck_hints(
    actions: Counter[str],
    page_views: Counter[str],
    approve_actions: int,
    report_actions: int,
) -> list[str]:
    hints: list[str] = []
    if not page_views and not actions:
        return hints
    conflicts = sum(
        count
        for action, count in actions.items()
        if "conflict" in action.lower() or action == "concurrency_conflict"
    )
    if conflicts:
        hints.append(f"Recorded {conflicts} concurrency conflict audit(s) — refresh UX risk.")
    if report_actions and approve_actions and report_actions > approve_actions * 2:
        hints.append("Reports outpace approvals — supervisor approval latency risk.")
    execution_views = page_views.get("/dashboard/console/execution", 0)
    overview_views = page_views.get("/dashboard/overview", 0)
    if execution_views > overview_views * 3 and overview_views > 0:
        hints.append("Heavy execution console use vs overview — possible dashboard bypass.")
    if sum(page_views.values()) >= 5:
        if page_views.get("/dashboard/console", 0) <= 1 and page_views.get(
            "/dashboard/console/activity",
            0,
        ) <= 1:
            hints.append(
                "Low planning console traffic — bootstrap friction or pre-seeded data.",
            )
    return hints
