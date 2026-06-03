# Stage 31 — Organizational Execution Intelligence Report

**Stage:** 31 — Organizational Execution Intelligence  
**Type:** Explainable cross-project heuristics (no ERP, no HR scoring, no ML agents)  
**Prerequisite:** Stage 30 Operational Coordination & Team Execution Intelligence complete

---

## Executive Summary

Stage 31 adds **organizational execution intelligence** across accessible projects: cross-project patterns, supervisor operational trends (audit-based, not HR scores), execution maturity bands, culture indicators, multi-project coordination pressure, and execution-capacity assessment. Delivery is **`GET /analytics/organizational-intelligence`** plus a lightweight **Organizational execution intelligence** overlay on Overview — workers are excluded.

| Area | Outcome |
| --- | --- |
| Cross-project execution analysis | Implemented |
| Organizational bottleneck detection | Implemented |
| Supervisor effectiveness trends | Implemented (audit JSONL, 7d) |
| Execution maturity signals | Six explainable components + band |
| Operational culture indicators | Rule-based, operational framing |
| Multi-project coordination visibility | Pressure snapshots + signals |
| Execution-capacity intelligence | BALANCED / PRESSURED / SATURATED |
| Organizational attention layer | Admin, supervisor, investor |
| Verification | `stage31_verification.py`, CI workflow |

---

## 1. Cross-Project Findings

### Method

- Analyze up to **`ORG_INTEL_MAX_PROJECTS`** (default 25) accessible projects.
- Admin: all projects; supervisor/investor: membership-scoped set.
- Aggregate SQL + Stage 28 `health_band` per project.

### Signal types

| Signal | Trigger (heuristic) | Meaning |
| --- | --- | --- |
| `recurring_blocker_types` | Open blockers; top types listed | Org-wide execution weakness |
| `workflow_slowdown_pattern` | Stalled steps ≥ project count | Repeated slowdown |
| `approval_bottleneck_pattern` | Overdue approvals ≥ 3 | Governance congestion |
| `execution_drift` | ≥ 2 projects `AT_RISK` (Stage 28) | Instability across portfolio |

### Comparison to Stage 28–30

| Stage | Scope |
| --- | --- |
| 28 | Single-project health |
| 29 | Single-project priorities |
| 30 | Single-project coordination |
| **31** | **Portfolio** patterns |

---

## 2. Organizational Bottleneck Findings

| Signal | When surfaced |
| --- | --- |
| `chronic_approval_congestion` | ≥ 2 overdue approvals org-wide |
| `blocker_choke_point` | ≥ 5 open blockers |
| `coordination_failure_pattern` | Stalled steps ≥ 2× project count |
| `execution_capacity_imbalance` | ≥ 10 pending approvals |

These identify **where the organization repeatedly struggles**, not individual blame.

---

## 3. Supervisor-Effectiveness Findings

### Data source

`data/operational_audit.jsonl` — last 7 days, `admin` / `supervisor` roles only.

### Metrics (operational, not HR)

| Field | Purpose |
| --- | --- |
| `approvals_7d` | Approval audit actions |
| `assignments_7d` | Assignment audit actions |
| `audit_actions_7d` | Total governance actions |
| `observation` | Plain-language trend line |
| `concentration_risk` | ≥ 60% of org audit share on one user |

### Example observations

- High approval activity while org pending queue is large → overload / catch-up batch.
- Balanced approvals + assignments → healthy handoff week.
- Concentration risk → **organizational dependency** on one account (training or staffing topic).

**Explicitly not:** performance ratings, rankings, or compensation signals.

---

## 4. Execution Maturity Findings

### Components (0–100 each, explained)

| Factor | Formula (conceptual) |
| --- | --- |
| `workflow_continuity` | % projects with IN_PROGRESS steps |
| `reporting_reliability` | % projects with reports in 7d |
| `approval_discipline` | % pending approvals not overdue |
| `blocker_responsiveness` | Penalty for open/recurring blockers |
| `coordination_consistency` | Penalty for approvals+blockers per project |
| `operational_recovery` | Penalty for aggregated stalled steps |

### Maturity bands

| Band | Score | Interpretation |
| --- | --- | --- |
| ESTABLISHED | ≥ 75 | Consistent execution rhythm |
| DEVELOPING | 55–74 | Gaps remain |
| EMERGING | 35–54 | Reporting/approval strengthening needed |
| STRAINED | < 35 | Org-wide review recommended |

**No fake AI score** — average of six transparent components.

---

## 5. Operational Culture Findings

Operational habits (not psychology):

| Indicator | Pattern |
| --- | --- |
| `delayed_approvals_habit` | Recurring overdue approvals |
| `ignored_blockers_pattern` | Many open blockers, few types |
| `reporting_inconsistency` | Reports < project count |
| `reactive_execution` | Reports active, approvals lag |
| `discipline_stable` | No major risks at thresholds |

---

## 6. Multi-Project Coordination Findings

### Project snapshots

Per project: `health_band`, `coordination_pressure` (low/medium/high), blockers, pending approvals, reports_7d, stalled steps — sorted by pressure.

### Portfolio signals

| Signal | Meaning |
| --- | --- |
| `competing_project_attention` | ≥ 2 high-pressure projects |
| `coordination_hotspot` | AT_RISK projects in portfolio |
| `operational_imbalance` | Many projects above medium pressure |

Supports **executive/investor** visibility without console redesign.

---

## 7. Execution-Capacity Findings

### Capacity bands

| Band | Heuristic |
| --- | --- |
| BALANCED | Load (pending+blockers) vs reports_7d reasonable |
| PRESSURED | Ratio ≥ 1.5 or ≥ 5 load units per project |
| SATURATED | Ratio ≥ 3 or ≥ 10 load units per project |

### Throughput inputs

- Approvals pending (governance load)
- Open blockers (execution friction)
- Daily reports last 7 days (field throughput proxy)

**No predictive ML** — explainable ratio only.

---

## 8. False-Positive Analysis

| Risk | Cause | Mitigation |
| --- | --- | --- |
| STRAINED maturity on pilot | One project, little data | Require ≥ 2 projects before exec escalation |
| Supervisor concentration | Single tester account | Multi-user pilot JSONL |
| AT_RISK drift | Stage 28 threshold tuning | Compare per-project before org action |
| Culture “ignored blockers” | Few categories by taxonomy | Review blocker_type taxonomy |
| Capacity SATURATED | Zero reports in 7d | Weekend/holiday calendar |
| 25-project cap | Large portfolios truncated | Raise `ORG_INTEL_MAX_PROJECTS` in ops env |

### Signal-noise balance

| Control | Value |
| --- | --- |
| Attention lines capped | 8 |
| Snapshots shown | 12 |
| Supervisor trends | Top 8 by audit volume |
| Worker exposure | None |

---

## 9. Recommended Stage 32

1. **Portfolio digest export** — weekly JSON/CSV of maturity + bottlenecks for executives (no new BI stack).
2. **Project drill-down links** — org snapshot → select project on overview (query param).
3. **Trend deltas** — compare maturity_score vs prior week from archived JSONL snapshots.
4. **Configurable org thresholds** — document `ORG_INTEL_MAX_PROJECTS`, capacity ratio env vars in ops playbook.
5. **Supervisor roster scope** — optional filter by supervisor username without HR scoring.
6. **Live pilot validation** — 30-day org intel review with contractor leadership; measure false-positive dismiss rate.

---

## Artifacts (Stage 31)

| Artifact | Path |
| --- | --- |
| Service | `backend/phase1/analytics/organizational_intelligence_service.py` |
| Schema | `backend/phase1/schemas/organizational_intelligence_schema.py` |
| API | `GET /analytics/organizational-intelligence` |
| Frontend | `OrganizationalIntelligencePanel.tsx` |
| Types | `frontend/lib/api/phase1/analytics.ts` |
| Role gate | `canViewOrganizationalIntelligence()` — not workers |
| Scripts | `stage31_verification.py`, `stage31_runtime_verification.py` |
| CI | `.github/workflows/stage31-ci.yml` |

---

## Verification Commands

```bash
set PYTHONPATH=.
set SKIP_STARTUP_VALIDATION=true
python backend/scripts/stage31_runtime_verification.py

cd frontend && npm run build
```

With PostgreSQL, admin token returns full `data_available: true` payload.

---

**Stage 31 complete.** Do not proceed to Stage 32 implementation within this deliverable scope.
