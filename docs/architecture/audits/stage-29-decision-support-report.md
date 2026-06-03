# Stage 29 — Decision Support & Operational Guidance Report

**Stage:** 29 — Decision Support & Operational Guidance  
**Type:** Explainable operational guidance (no LLM, no architecture redesign)  
**Prerequisite:** Stage 28 Operational Intelligence & Predictive Runtime complete

---

## Executive Summary

Stage 29 adds **deterministic decision support** on top of Stage 28 intelligence: explainable priority ordering, supervisor guidance lines, approval queue ordering, blocker resolution hints, workload imbalance signals, and actionable recommendations. Delivery is a **`decision_support` block** on the existing operational-intelligence API plus a lightweight overlay on the Overview **Operational attention** panel.

| Area | Outcome |
| --- | --- |
| Operational priority ranking | Implemented (score + rank + explanation) |
| Supervisor attention guidance | Implemented |
| Approval queue prioritization | Implemented (oldest-first, overdue flag) |
| Blocker resolution guidance | Implemented |
| Workload imbalance | Implemented (audit JSONL, 7-day window) |
| Runtime recommendations | Implemented (rule-based, no AI) |
| Attention overlay | Extended `OperationalAttentionPanel` |
| Verification | `stage29_verification.py`, `stage29_runtime_verification.py` |

**Not in scope:** autonomous agents, LLM assistants, dashboard redesign, enterprise recommendation engines.

---

## 1. Operational Priority Logic

### Design principles

- **Deterministic** — same DB state → same ordering.
- **Explainable** — every item has `priority_score`, `explanation`, `suggested_action`.
- **No black box** — scores are category base + capped day increments.

### Category base scores (illustrative)

| Category | Base logic | Typical score range |
| --- | --- | --- |
| `blocked_workflow` (CRITICAL/HIGH blocker) | 88 + min(12, age days) | 88–100 |
| `stalled_approval` | 75 + min(20, days pending) when overdue | 75–95 |
| `blocked_workflow` (stalled step) | 68 + idle days; +5 if WOs exist | 68–83 |
| `rework` | Fixed 62 when REWORK_REQUIRED steps exist | 62 |
| `inactive_work_order` | 48 + min(12, idle days) | 48–60 |
| `delayed_reporting` | 42 when 0 reports in 7d but WOs exist | 42 |

Items are sorted by **`priority_score` descending**, then title; ranks 1–15 returned.

### Implementation

`backend/phase1/analytics/decision_support_service.py` — `build_project_decision_support()`.

### Comparison to Stage 28

Stage 28 **`attention_needed`** lists up to five heterogeneous items without global rank. Stage 29 **`priority_queue`** unifies blockers, approvals, stagnation, WOs, and reporting into one ordered list supervisors can act on.

---

## 2. Attention-Guidance Findings

### Supervisor guidance strings (examples)

Generated from live counts and Stage 28 health band:

- `N approval(s) delayed more than {OPS_APPROVAL_DELAY_DAYS} days — prioritize queue head before new assignments.`
- `N HIGH/CRITICAL blocker(s) open — field execution risk until resolved.`
- `Blocker accumulation: N open on this project.`
- `Project health AT_RISK (Stage 28) — schedule a supervisor review this week.`
- `Approval activity today without matching report submissions — verify field reporting.`

When no triggers fire:

- `No supervisor escalation triggers at current thresholds — continue routine monitoring.`

### UI

Overview → **Operational attention** → **Supervisor guidance** (admin/supervisor) or **Operational summary** (investor, top 3 lines).

### Usefulness (audit)

| Criterion | Assessment |
| --- | --- |
| Operational clarity | High — full sentences, no jargon scores alone |
| Intervention usefulness | High when Postgres + real data |
| Overload risk | Medium — capped lists; recommendations max 8 |

---

## 3. Approval Prioritization Findings

### Queue ordering

- All `PENDING` / `UNDER_REVIEW` approvals for the project.
- Sorted by **`approval.updated_at` ascending** (oldest first).
- Each row: `days_pending`, `overdue` vs `OPS_APPROVAL_DELAY_DAYS` (default 5), `priority_score`, `suggested_action`.

### Bottleneck signals

- **Delayed count** feeds supervisor guidance and recommendations.
- **Backlog vs reports** — inherited from Stage 28 `approval_backlog_vs_reports` signal; recommendations reference queue depth ≥ 5.

### Downstream delay (explainable)

Overdue approvals receive higher priority scores than fresh pending items — proxy for downstream step blockage without simulating CPM.

---

## 4. Blocker Guidance Findings

| Signal type | When | Message pattern |
| --- | --- | --- |
| `repeated_blocker_categories` | Open blockers exist | Top 3 types with counts |
| `longest_unresolved_blocker` | Age ≥ stall threshold | Longest open blocker title + step/activity |
| `rising_blocker_density` | ≥ 4 open simultaneously | Execution hotspot warning |

Aligned with Stage 28 **`blocker_trends`** but oriented toward **resolution action** (what to clear first).

### False-positive risk

- Same blocker type twice ≠ always systemic — may be duplicate categorization.
- **Mitigation:** `false_positive_notes` on API; supervisor confirms in field.

---

## 5. Workload Imbalance Findings

### Data source

`data/operational_audit.jsonl` (Stage 27+), project-scoped, 7-day window.

| Imbalance type | Rule | Severity |
| --- | --- | --- |
| `supervisor_concentration` | One user ≥ 70% of actions, ≥ 3 events | warning |
| `approval_vs_reporting` | Approvals ≥ 5 and reports < half of approvals | warning |
| `neglected_field_activity` | Zero worker actions, ≥ 5 admin/supervisor actions | info |

### Limitations

- Empty or sparse JSONL → **no imbalance rows** (not a failure).
- Audit reflects API mutations, not offline manual work — documented in false-positive notes.

### Stage 28 cross-check

If Stage 28 shows `approval_burst` anomaly but imbalance shows supervisor concentration, treat as **catch-up batch** not necessarily overload.

---

## 6. Runtime Recommendation Logic

Recommendations are **if-then rules** over Stage 28 intel + decision context:

| Condition | Severity | Example message |
| --- | --- | --- |
| delayed approvals ≥ 3 | critical | Review stalled approvals before new assignments |
| delayed ≥ 1 | warning | Clear queue head first |
| pending ≥ 5 | warning | Approval backlog — batch review |
| critical blocker trend | critical | Resolve blockers before new assignments |
| reporting_gap component | warning | Daily reporting frequency dropping |
| health band AT_RISK | critical | Supervisor intervention this week |
| Stage 28 forecast `approval_backlog_risk` | warning | Align supervisor capacity |

Each item includes **`rationale`** citing threshold or Stage 28 signal.

**No** chat persona, **no** generative text.

---

## 7. False-Positive Analysis

| Signal | False-positive cause | Mitigation |
| --- | --- | --- |
| High priority score on old PLANNED step | Planning-heavy pilot, no execution yet | Compare with `workflow_starvation` (Stage 28) |
| Overdue approval | Clock/timezone vs `updated_at` | Tune `OPS_APPROVAL_DELAY_DAYS` |
| Supervisor concentration | Single pilot tester account | Require multi-user JSONL before escalation |
| Reporting gap | Weekend/holiday calendar | Extend window in ops config (future) |
| Workload imbalance | JSONL from simulation bursts | Cross-check with adoption summary (Stage 27) |

### Attention fatigue risk

| Factor | Level | Control |
| --- | --- | --- |
| Recommendation count | Low | Max 8, deduplicated |
| Priority queue length | Medium | Top 15 only |
| Investor view | Low | Top 5 priorities, no approval queue |
| Duplicate Stage 28 detail | Medium | Investor/supervisor: collapse signal detail in `<details>` |

---

## 8. Operational Usefulness Findings

| Role | What they get | Value |
| --- | --- | --- |
| **Admin** | Full queue, workload, recommendations | Portfolio intervention |
| **Supervisor** | Same as admin on assigned projects | Daily standup ordering |
| **Investor** | Health + top priorities + summary guidance | Risk visibility without ops noise |
| **Worker** | Intelligence API allowed if project member; panel hidden by policy on overview for non-readers | N/A on overview |

### Compared to Stage 28

| Stage 28 | Stage 29 |
| --- | --- |
| Health score & band | Unchanged |
| Signals & forecasts | Unchanged |
| Attention list (5 items) | Superseded for action by **priority_queue** |
| — | **What to do next** recommendations |
| — | **Approval queue** ordering |

### Pilot readiness

- **Useful without ML** when PostgreSQL has approvals/blockers/reports.
- **Degraded without DB** — guidance strings explain Postgres requirement; recommendations still derived from Stage 28 JSONL-only intel.

---

## 9. Recommended Stage 30

1. **Deep-link actions** — priority items link to `execution?focus=approve` with step pre-selection (query param), not just activity list.
2. **Configurable thresholds UI** — env vars `OPS_STALL_DAYS` / `OPS_APPROVAL_DELAY_DAYS` documented in ops playbook; optional admin read-only display on overview.
3. **Weekly adoption + decision digest** — merge Stage 27 adoption summary with top 3 priorities per project for email/export (no new platform).
4. **False-positive feedback loop** — “dismiss/snooze” on recommendation (JSONL only, no new DB entity) to measure noise rate.
5. **Multi-project supervisor dashboard** — aggregate priority queue across authorized projects (read-only list endpoint).
6. **Human pilot validation** — run 2-week live pilot; measure time-to-first-approval after guidance vs Stage 25 baseline metrics.

---

## Artifacts (Stage 29)

| Artifact | Path |
| --- | --- |
| Decision support service | `backend/phase1/analytics/decision_support_service.py` |
| Schemas | `backend/phase1/schemas/operational_intelligence_schema.py` |
| API (embedded) | `GET /analytics/projects/{id}/operational-intelligence` |
| Frontend overlay | `frontend/components/operational/OperationalAttentionPanel.tsx` |
| Types | `frontend/lib/api/phase1/intelligence.ts` |
| Role policy | `canViewSupervisorDecisionDetail()` |
| Scripts | `stage29_verification.py`, `stage29_decision_support.py`, `stage29_runtime_verification.py` |
| CI | `.github/workflows/stage29-ci.yml` |

---

## Verification Commands

```bash
# Shape + decision_support (degraded OK without Postgres)
set PYTHONPATH=.
set SKIP_STARTUP_VALIDATION=true
python backend/scripts/stage29_runtime_verification.py

# Full decision payload for a real project
set STAGE29_PROJECT_ID=<uuid>
python backend/scripts/stage29_decision_support.py

# Frontend
cd frontend && npm run build
```

---

**Stage 29 complete.** Do not proceed to Stage 30 implementation within this deliverable scope.
