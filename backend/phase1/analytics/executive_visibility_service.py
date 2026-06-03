"""Executive operational awareness — compresses Stage 31 org intel (Stage 32)."""



from __future__ import annotations



from collections import Counter

from datetime import timedelta

from typing import Any

from uuid import UUID



from sqlalchemy.orm import Session



from backend.phase1.analytics.audit_store import load_audit_records

from backend.phase1.analytics.organizational_intelligence_service import (

    build_organizational_intelligence,

)

from backend.phase1.analytics.operational_intelligence_service import _utc_now





def _empty_executive(note: str) -> dict[str, Any]:

    return {

        "generated_at": _utc_now().isoformat(),

        "data_available": False,

        "executive_summary": note,

        "portfolio_health": {

            "overall_band": "UNKNOWN",

            "summary": note,

            "projects_analyzed": 0,

            "health_distribution": {},

            "coordination_pressure_distribution": {},

            "maturity_band": "UNKNOWN",

            "capacity_band": "UNKNOWN",

            "deteriorating_project_codes": [],

            "stable_project_codes": [],

        },

        "strategic_risks": [],

        "trend_narratives": [],

        "leadership_priorities": [],

        "pressure_indicators": [],

        "strategic_attention": [note],

        "false_positive_notes": [

            "Executive layer compresses organizational intelligence — not a BI platform.",

            "Trend narratives use audit/telemetry windows when JSONL exists; otherwise current-state only.",

            "Workers and supervisors use project/org views — not this endpoint.",

        ],

    }





def build_executive_visibility(

    db: Session | None,

    accessible_project_ids: set[UUID] | None,

) -> dict[str, Any]:

    org = build_organizational_intelligence(db, accessible_project_ids)

    if not org.get("data_available"):

        empty = _empty_executive(

            org.get("maturity_summary")

            or "Connect PostgreSQL for executive portfolio visibility.",

        )

        empty["portfolio_health"]["maturity_band"] = org.get("maturity_band", "UNKNOWN")

        empty["portfolio_health"]["capacity_band"] = org.get("capacity_band", "UNKNOWN")

        return empty



    portfolio = _portfolio_health(org)

    risks = _strategic_risks(org)

    narratives = _trend_narratives(org)

    pressures = _pressure_indicators(org)

    priorities = _leadership_priorities(org, portfolio, risks, pressures)

    summary = _executive_summary(org, portfolio)

    attention = _strategic_attention(summary, priorities, org)



    return {

        "generated_at": org["generated_at"],

        "data_available": True,

        "executive_summary": summary,

        "portfolio_health": portfolio,

        "strategic_risks": risks[:6],

        "trend_narratives": narratives[:5],

        "leadership_priorities": priorities[:6],

        "pressure_indicators": pressures[:6],

        "strategic_attention": attention[:5],

        "false_positive_notes": [

            *org.get("false_positive_notes", [])[:2],

            "Executive summaries cap lists at 5–6 items to reduce attention fatigue.",

            "Portfolio band is heuristic — confirm AT_RISK projects in Stage 28 before escalation.",

            "Audit-based trends need sufficient operational_audit.jsonl history (7–14 days).",

        ],

    }





def _portfolio_health(org: dict[str, Any]) -> dict[str, Any]:

    snapshots = org.get("project_snapshots", [])

    health_dist: Counter[str] = Counter()

    pressure_dist: Counter[str] = Counter()

    deteriorating: list[str] = []

    stable: list[str] = []



    for snap in snapshots:

        band = snap.get("health_band", "UNKNOWN")

        health_dist[band] += 1

        pressure = snap.get("coordination_pressure", "unknown")

        pressure_dist[pressure] += 1

        code = snap.get("project_code", "")

        if band in ("AT_RISK", "ATTENTION") or pressure == "high":

            deteriorating.append(code)

        elif band == "GOOD" and pressure in ("low", "medium"):

            stable.append(code)



    at_risk = health_dist.get("AT_RISK", 0)

    attention = health_dist.get("ATTENTION", 0)

    maturity = org.get("maturity_band", "UNKNOWN")

    capacity = org.get("capacity_band", "UNKNOWN")

    n = org.get("projects_analyzed", 0)



    if (

        at_risk >= 2

        or maturity == "STRAINED"

        or capacity == "SATURATED"

    ):

        overall = "CRITICAL"

        summary = (

            f"Portfolio under strategic stress — {at_risk} AT_RISK project(s), "

            f"maturity {maturity}, capacity {capacity}."

        )

    elif at_risk >= 1 or attention >= 2 or capacity == "PRESSURED" or maturity in (

        "EMERGING",

        "STRAINED",

    ):

        overall = "CAUTION"

        summary = (

            f"Portfolio needs leadership attention — mixed health across {n} project(s); "

            f"coordination and approval queues warrant review."

        )

    elif maturity in ("ESTABLISHED", "DEVELOPING") and capacity == "BALANCED":

        overall = "HEALTHY"

        summary = (

            f"Portfolio execution broadly healthy across {n} project(s) — "

            "monitor hotspots only."

        )

    else:

        overall = "STABLE"

        summary = (

            f"Portfolio stable at pilot scale ({n} project(s)) — "

            "no org-wide deterioration signal at current thresholds."

        )



    return {

        "overall_band": overall,

        "summary": summary,

        "projects_analyzed": n,

        "health_distribution": dict(health_dist),

        "coordination_pressure_distribution": dict(pressure_dist),

        "maturity_band": maturity,

        "capacity_band": capacity,

        "deteriorating_project_codes": deteriorating[:6],

        "stable_project_codes": stable[:6],

    }





def _strategic_risks(org: dict[str, Any]) -> list[dict[str, Any]]:

    seen: set[str] = set()

    merged: list[dict[str, Any]] = []

    severity_order = {"critical": 0, "warning": 1, "info": 2}



    for source in (

        org.get("organizational_bottlenecks", []),

        org.get("cross_project_findings", []),

        org.get("multi_project_coordination", []),

        org.get("culture_indicators", []),

    ):

        for item in source:

            st = item.get("signal_type", "")

            if st in seen or item.get("severity") == "info" and len(merged) >= 4:

                continue

            seen.add(st)

            merged.append(item)



    merged.sort(key=lambda x: severity_order.get(x.get("severity", "info"), 9))

    if not merged:

        merged.append(

            {

                "signal_type": "no_elevated_org_risk",

                "severity": "info",

                "message": "No elevated organization-wide operational risks at current thresholds.",

                "evidence": "Aggregated Stage 31 heuristics.",

                "count": 0,

            },

        )

    return merged





def _audit_week_buckets() -> tuple[int, int, int, int]:

    """Approvals and assign actions: prior 7d vs previous 7d (audit JSONL)."""

    now = _utc_now()

    recent_start = (now - timedelta(days=7)).date().isoformat()

    prior_start = (now - timedelta(days=14)).date().isoformat()

    recent_approve = recent_assign = prior_approve = prior_assign = 0



    for record in load_audit_records():

        occurred = (record.get("occurred_at") or "")[:10]

        if occurred < prior_start:

            continue

        action = (record.get("action") or "").lower()

        if "approve" in action:

            if occurred >= recent_start:

                recent_approve += 1

            else:

                prior_approve += 1

        if "assign" in action:

            if occurred >= recent_start:

                recent_assign += 1

            else:

                prior_assign += 1



    return recent_approve, prior_approve, recent_assign, prior_assign





def _trend_narratives(org: dict[str, Any]) -> list[dict[str, Any]]:

    narratives: list[dict[str, Any]] = []

    snapshots = org.get("project_snapshots", [])

    high_pressure = [s for s in snapshots if s.get("coordination_pressure") == "high"]

    if len(high_pressure) >= 2:

        codes = ", ".join(s["project_code"] for s in high_pressure[:4])

        narratives.append(

            {

                "narrative_id": "coordination_pressure_cluster",

                "trend_direction": "worsening",

                "message": f"Coordination pressure concentrated in {len(high_pressure)} project(s): {codes}.",

                "evidence": "Per-project pressure heuristic (approvals + blockers + stalled steps).",

            },

        )



    delayed = sum(

        1

        for item in org.get("cross_project_findings", [])

        if item.get("signal_type") == "approval_bottleneck_pattern"

    )

    bottlenecks = org.get("organizational_bottlenecks", [])

    chronic = any(

        b.get("signal_type") == "chronic_approval_congestion" for b in bottlenecks

    )

    recent_a, prior_a, recent_g, prior_g = _audit_week_buckets()



    if chronic:

        if prior_a > 0 and recent_a < prior_a * 0.7:

            narratives.append(

                {

                    "narrative_id": "approval_delay_easing",

                    "trend_direction": "improving",

                    "message": "Approval activity increased while overdue queue remains — possible catch-up after workflow focus.",

                    "evidence": f"Audit approvals {recent_a} (7d) vs {prior_a} prior week; org bottlenecks still flagged.",

                },

            )

        else:

            narratives.append(

                {

                    "narrative_id": "approval_saturation",

                    "trend_direction": "worsening" if recent_a <= prior_a else "stable",

                    "message": "Approval-system saturation persists organization-wide.",

                    "evidence": "Stage 31 chronic_approval_congestion + cross-project approval pattern.",

                },

            )

    elif delayed and recent_a > prior_a and prior_a > 0:

        narratives.append(

            {

                "narrative_id": "approval_throughput_up",

                "trend_direction": "improving",

                "message": "Supervisor approval throughput rose week-over-week while some overdue items remain.",

                "evidence": f"Audit approvals {recent_a} vs {prior_a} (prior 7d window).",

            },

        )



    maturity = org.get("maturity_band", "UNKNOWN")

    strained_projects = [

        s for s in snapshots if s.get("health_band") == "AT_RISK"

    ]

    if maturity in ("EMERGING", "STRAINED") and strained_projects:

        codes = ", ".join(s["project_code"] for s in strained_projects[:3])

        narratives.append(

            {

                "narrative_id": "maturity_deterioration_hotspots",

                "trend_direction": "worsening",

                "message": f"Execution maturity {maturity} with deteriorating health in: {codes}.",

                "evidence": f"Org maturity score {org.get('maturity_score')}/100; Stage 28 AT_RISK bands.",

            },

        )



    if recent_g > prior_g * 1.5 and prior_g > 0 and org.get("capacity_band") == "PRESSURED":

        narratives.append(

            {

                "narrative_id": "assignment_surge_capacity",

                "trend_direction": "worsening",

                "message": "Assignment activity rose while execution capacity is PRESSURED — fragmentation risk.",

                "evidence": f"Audit assignments {recent_g} vs {prior_g}; capacity {org.get('capacity_band')}.",

            },

        )



    if not narratives:

        narratives.append(

            {

                "narrative_id": "portfolio_stable_narrative",

                "trend_direction": "stable",

                "message": "No worsening cross-project trend detected at current telemetry depth.",

                "evidence": "Stage 31 snapshot + audit window (if JSONL present).",

            },

        )

    return narratives





def _pressure_indicators(org: dict[str, Any]) -> list[dict[str, Any]]:

    indicators: list[dict[str, Any]] = []

    capacity = org.get("capacity_band", "UNKNOWN")

    if capacity in ("PRESSURED", "SATURATED"):

        indicators.append(

            {

                "indicator_type": "execution_capacity",

                "severity": "critical" if capacity == "SATURATED" else "warning",

                "message": org.get("capacity_summary", "Capacity stress detected."),

                "evidence": f"Capacity band {capacity} (Stage 31).",

            },

        )



    for item in org.get("organizational_bottlenecks", [])[:3]:

        st = item.get("signal_type", "")

        if st == "chronic_approval_congestion":

            indicators.append(

                {

                    "indicator_type": "approval_congestion",

                    "severity": item.get("severity", "warning"),

                    "message": item.get("message", ""),

                    "evidence": item.get("evidence", ""),

                },

            )

        elif st == "blocker_choke_point":

            indicators.append(

                {

                    "indicator_type": "blocker_density",

                    "severity": item.get("severity", "warning"),

                    "message": item.get("message", ""),

                    "evidence": item.get("evidence", ""),

                },

            )

        elif st == "coordination_failure_pattern":

            indicators.append(

                {

                    "indicator_type": "coordination_overload",

                    "severity": item.get("severity", "warning"),

                    "message": item.get("message", ""),

                    "evidence": item.get("evidence", ""),

                },

            )



    concentration = [

        t for t in org.get("supervisor_trends", []) if t.get("concentration_risk")

    ]

    if concentration:

        user = concentration[0].get("username", "supervisor")

        indicators.append(

            {

                "indicator_type": "supervisor_overload_concentration",

                "severity": "warning",

                "message": f"Operational dependency concentrated on {user} (audit share, not HR score).",

                "evidence": concentration[0].get("observation", ""),

            },

        )



    fragmented = sum(

        1

        for s in org.get("culture_indicators", [])

        if s.get("signal_type") in ("reporting_inconsistency", "reactive_execution")

    )

    if fragmented >= 2:

        indicators.append(

            {

                "indicator_type": "operational_fragmentation",

                "severity": "info",

                "message": "Reporting and governance cadence misaligned across projects.",

                "evidence": "Multiple culture indicators from Stage 31.",

            },

        )



    if not indicators:

        indicators.append(

            {

                "indicator_type": "pressure_balanced",

                "severity": "info",

                "message": "Organizational pressure within expected pilot bounds.",

                "evidence": "No saturation signals at current thresholds.",

            },

        )

    return indicators





def _leadership_priorities(

    org: dict[str, Any],

    portfolio: dict[str, Any],

    risks: list[dict[str, Any]],

    pressures: list[dict[str, Any]],

) -> list[dict[str, Any]]:

    priorities: list[dict[str, Any]] = []

    rank = 1



    def add(

        concern: str,

        level: str,

        evidence: str,

        focus: str,

    ) -> None:

        nonlocal rank

        priorities.append(

            {

                "rank": rank,

                "concern": concern,

                "attention_level": level,

                "evidence": evidence,

                "suggested_focus": focus,

            },

        )

        rank += 1



    if portfolio.get("overall_band") == "CRITICAL":

        add(

            "Portfolio execution under strategic stress",

            "immediate",

            portfolio.get("summary", ""),

            "Executive/supervisor review of AT_RISK projects and approval queues before new commitments.",

        )

    if org.get("capacity_band") == "SATURATED":

        add(

            "Execution-capacity saturation",

            "immediate",

            org.get("capacity_summary", ""),

            "Pause non-essential assignments; clear approvals and blockers org-wide.",

        )

    for risk in risks:

        if risk.get("severity") != "critical" or rank > 5:

            continue

        add(

            risk.get("message", "Critical operational risk"),

            "immediate",

            risk.get("evidence", ""),

            "Target bottleneck clearance with accountable owners per project.",

        )

        if rank > 5:

            break



    if org.get("maturity_band") in ("EMERGING", "STRAINED"):

        add(

            f"Organizational maturity {org.get('maturity_band')}",

            "planned",

            org.get("maturity_summary", ""),

            "Strengthen reporting cadence and approval discipline using Stage 31 maturity components.",

        )



    codes = portfolio.get("deteriorating_project_codes", [])

    if codes and rank <= 6:

        add(

            f"Hotspot projects: {', '.join(codes[:4])}",

            "planned",

            "High coordination pressure or AT_RISK/ATTENTION health bands.",

            "Deep-dive Stage 28 operational intelligence per hotspot project.",

        )



    for pressure in pressures:

        if pressure.get("indicator_type") == "supervisor_overload_concentration" and rank <= 6:

            add(

                "Supervisor load concentration",

                "monitor",

                pressure.get("evidence", ""),

                "Distribute approval/assignment load; avoid single-account dependency.",

            )

            break



    if not priorities:

        add(

            "Continue portfolio monitoring",

            "stable",

            "No leadership escalation triggers at current thresholds.",

            "Maintain Stage 27–31 telemetry; revisit if AT_RISK count rises.",

        )

    return priorities





def _executive_summary(org: dict[str, Any], portfolio: dict[str, Any]) -> str:

    band = portfolio.get("overall_band", "UNKNOWN")

    n = portfolio.get("projects_analyzed", 0)

    maturity = org.get("maturity_band", "UNKNOWN")

    capacity = org.get("capacity_band", "UNKNOWN")

    at_risk = portfolio.get("health_distribution", {}).get("AT_RISK", 0)



    line1 = (

        f"Portfolio {band} across {n} accessible project(s) — "

        f"org maturity {maturity}, capacity {capacity}."

    )

    if at_risk:

        line2 = (

            f"{at_risk} project(s) at AT_RISK; prioritize interventions listed under leadership priorities."

        )

    elif band in ("HEALTHY", "STABLE"):

        line2 = "No org-wide deterioration requiring immediate executive escalation."

    else:

        line2 = "Review strategic risks and pressure indicators before expanding workload."

    return f"{line1} {line2}"





def _strategic_attention(

    summary: str,

    priorities: list[dict[str, Any]],

    org: dict[str, Any],

) -> list[str]:

    lines = [summary]

    for p in priorities[:3]:

        lines.append(f"[{p['attention_level'].upper()}] {p['concern']}")

    for note in org.get("organizational_attention", [])[:2]:

        if note not in lines:

            lines.append(note)

    return lines

