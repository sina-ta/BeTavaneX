# COSC — Event Taxonomy

> What counts as an "event" in BetavanX today, where it lives, and what it means.
>
> **The system is not event-sourced.** No state is rebuilt from events. The
> authoritative state is the PostgreSQL row set. Events here are one of three
> things: (1) audit/usage **records** written *after* a state change, (2) **logged
> alerts/warnings**, and (3) **derived signals** computed on demand by analytics.
> All three are observational, never authoritative.

There are four event families:

1. Operational audit records (mutation log)
2. Usage events (frontend activity log)
3. Operational alerts (warning logs)
4. Derived operational signals (analytics output)

---

## 1. Operational audit records

Written by `auth/operational_audit.py::log_operational_action`, mirrored to JSONL
by `analytics/audit_store.py` (`OPERATIONAL_AUDIT_JSONL_PATH`, default
`data/operational_audit.jsonl`). Each mutation route emits one record **after** a
successful (or conflicting) operation.

### Record shape

```json
{
  "occurred_at": "<iso8601 utc>",
  "username": "<actor>",
  "role": "<admin|supervisor|worker|investor>",
  "mutation_category": "planning|execution|governance|query|conflict",
  "action": "<verb>",
  "project_id": "<uuid|null>",
  "resource_type": "<string|null>",
  "resource_id": "<uuid|null>",
  "detail": { }
}
```

### Mutation categories (the top-level taxonomy)

| Category | Meaning | Emitting operations (observed) |
|---|---|---|
| `planning` | Intent created | `create_project` (and other planning creates) |
| `execution` | Field/coordination action | `assign_work_order`, `submit_daily_report` |
| `governance` | Authority decision | `approve_workflow_step` |
| `query` | Read tracked as activity | (reserved category; reads are mostly via usage events) |
| `conflict` | Optimistic-lock collision | emitted by `log_concurrency_conflict` on `ConcurrencyConflictError` |

### Known action verbs (resource_type → action)

| action | mutation_category | resource_type | Source |
|---|---|---|---|
| `create_project` | planning | project | planning_router |
| `assign_work_order` | execution | work_order | runtime_router |
| `submit_daily_report` | execution | daily_report | runtime_router |
| `approve_workflow_step` | governance | workflow_step | runtime_router |

Conflicts reuse the same `action` (e.g. `assign_work_order`) but with
`mutation_category = "conflict"` and a `detail.conflict_resource_id`.

### Semantics

- **Append-only.** Records are never updated or deleted.
- **After-the-fact.** A record proves an action was attempted/committed; the row
  state is still the source of truth.
- **Attribution.** `username` + `role` are the actor identity; there is no FK, so
  the record is self-contained.
- **Analytics input.** Audit JSONL is read back by intelligence services for
  conflict spikes, approval/report cadence, and workload imbalance.

---

## 2. Usage events

Written by `analytics/usage_store.py::append_usage_event` to JSONL
(`OPERATIONAL_USAGE_PATH`, default `data/operational_usage.jsonl`). These capture
**UI/navigation activity**, not domain mutations.

### Record shape

```json
{
  "recorded_at": "<iso8601 utc>",
  "username": "<actor>",
  "role": "<role>",
  "event_type": "<string>",
  "page_path": "<route>",
  "session_id": "<string|null>",
  "referrer_path": "<string|null>",
  "project_id": "<uuid|null>"
}
```

### Semantics

- Tracks adoption/engagement (e.g. dashboard overview views).
- Used by `adoption_service` and cross-referenced by intelligence (e.g.
  "mutations without overview page views" → `inactive_dashboard` signal).
- Append-only, observational, non-authoritative.

---

## 3. Operational alerts (warning logs)

Emitted by `auth/operational_alerts.py` to the logger (not persisted as domain
data). They fire **at the moment a conflicting action is rejected**.

| Alert | Trigger |
|---|---|
| `duplicate_assignment` | second attempt to link the same `(work_order, workflow_step)` |
| `duplicate_approval` | second `APPROVED` approval of the same `approval_type` on a step |

These accompany a raised `ValueError`/conflict; they are diagnostic, not state.

---

## 4. Derived operational signals (analytics)

These are **computed on demand** from DB rows + audit/usage JSONL by the analytics
services. They are not stored events — each request recomputes them. They share a
common signal shape:

```json
{ "signal_type": "...", "severity": "info|warning|critical", "message": "...", "evidence": "...", "count": N }
```

### 4a. Stagnation signals (`operational_intelligence_service`)

| signal_type | Meaning | Threshold |
|---|---|---|
| `stalled_workflow_steps` | steps in active statuses untouched > `OPS_STALL_DAYS` (default 7) | `updated_at` age |
| `rework_required_steps` | steps in `REWORK_REQUIRED` | presence |
| `inactive_work_orders` | work orders stuck in `CREATED`/`ASSIGNED` past stall cutoff | `updated_at` age |

Active step statuses for stall = `{IN_PROGRESS, INSPECTION_PENDING, REWORK_REQUIRED, PLANNED}`.

### 4b. Approval signals

| signal_type | Meaning |
|---|---|
| `delayed_pending_approvals` | approvals `PENDING`/`UNDER_REVIEW` older than `OPS_APPROVAL_DELAY_DAYS` (default 5) |
| `approval_backlog_vs_reports` | pending approvals exceed reports in last 7 days |

### 4c. Blocker signals

| signal_type | Meaning |
|---|---|
| `open_blockers` | blockers in open set `{OPEN, ACKNOWLEDGED, MITIGATION_IN_PROGRESS, REOPENED}` (critical if any HIGH/CRITICAL) |
| `long_lived_blockers` | open blockers with `detected_date` age ≥ stall days |

### 4d. Anomaly signals

| signal_type | Meaning | Source |
|---|---|---|
| `concurrency_spike` | ≥2 conflict audit records in 7 days | audit JSONL |
| `duplicate_reporting_spike` | ≥5 report-submission audits today | audit JSONL |
| `workflow_starvation` | ≥5 `PLANNED` steps with zero `IN_PROGRESS` | DB |
| `inactive_dashboard` | ≥5 mutations but zero overview page views | audit + usage JSONL |
| `approval_burst` | ≥4 approval audits same day | audit JSONL |

### 4e. Health rollup (`health.band`)

A 0–100 score with deductions per factor (`critical_blockers`, `stalled_steps`,
`approval_delays`, `inactive_work_orders`, `reporting_gap`) mapped to a band:

| Band | Score | Meaning |
|---|---|---|
| `GOOD` | ≥75 | within expected pilot bounds |
| `ATTENTION` | 50–74 | several signals need supervisor review |
| `AT_RISK` | <50 | multiple stagnation/blocker signals |
| `UNKNOWN` | — | DB unavailable |

### 4f. Decision-support signals (`decision_support_service`)

Deterministic, no ML. Produces a ranked `priority_queue` of categories:

| category | Source condition |
|---|---|
| `stalled_approval` | overdue pending approval |
| `blocked_workflow` | open blocker on step, or stalled step |
| `inactive_work_order` | stale `CREATED`/`ASSIGNED` work order |
| `delayed_reporting` | no daily reports in 7 days with work orders present |
| `rework` | steps in `REWORK_REQUIRED` |

Plus `approval_queue` (ordered by oldest pending), `supervisor_guidance`,
`blocker_guidance`, `workload_imbalance`, and `recommendations`. Scores are
`base category weight + capped day increment` — fully explainable.

### 4g. Coordination signals (`coordination_intelligence_service`)

Cross-role handoff analysis. Bands `ALIGNED / FRAGMENTED / STRESSED / UNKNOWN`.

| signal family | examples |
|---|---|
| bottlenecks | `blocked_execution_chain`, `approval_coordination_delay` |
| cross_role_dependencies | `approval_backlog`, `delayed_approval_chain`, `reporting_handoff`, `assign_report_gap` |
| synchronization | `execution_drift`, `coordination_fragmentation`, `isolated_stalled_areas` |
| handoff_risks | `blocked_execution_chain`, `incomplete_field_handoff`, `approval_handoff_pending` |
| communication_gaps | `rework_clarification_loop`, `unresolved_blocker_communication`, `clarification_loop` |

---

## Event semantics summary

| Family | Persisted? | Authoritative? | Mutable? | Purpose |
|---|---|---|---|---|
| Audit records | JSONL (append-only) | No | No | prove mutations happened; feed analytics |
| Usage events | JSONL (append-only) | No | No | adoption/engagement |
| Alerts | logs only | No | No | diagnose rejected conflicts |
| Derived signals | not persisted (recomputed) | No | n/a | operational interpretation |

### Boundary rules for events

- Events are **produced after** state changes, never as the change itself.
- No consumer rebuilds domain state from events (no event sourcing).
- Thresholds (`OPS_STALL_DAYS`, `OPS_APPROVAL_DELAY_DAYS`) are environment-tunable;
  signals are heuristics with stated `false_positive_notes`, not facts.
- Severity (`info/warning/critical`) is advisory; it triggers no automatic action.
