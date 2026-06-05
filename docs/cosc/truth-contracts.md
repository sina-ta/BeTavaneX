# COSC — Truth Contracts

> Where authoritative truth lives, who is allowed to write it, and which values
> are derived (and therefore must never be trusted as primary). Extracted from the
> repository layer, services, schemas, and the optimistic-concurrency mechanism.

## The single source of truth

**PostgreSQL is the only authoritative store for domain state.** Every other
representation — runtime views, progress numbers, analytics signals, audit/usage
JSONL — is derived from or downstream of the database rows.

```
PostgreSQL rows  ── authoritative ──▶ everything else is a projection
```

JSONL files (`operational_audit.jsonl`, `operational_usage.jsonl`) are **append-only
observation logs**, not sources of truth. They can be deleted/rotated without
affecting domain correctness; analytics simply degrade.

---

## Truth ownership by concept

| Concept | Authoritative field(s) | Owner (only writer) | Derived elsewhere? |
|---|---|---|---|
| Project header/status | `projects` row | `PlanningUseCases` via repo | — |
| WBS / Location / BOQ | their rows | `PlanningUseCases` | — |
| ActivityInstance | `activity_instances` row | `PlanningUseCases` | progress is derived, not stored |
| WorkflowStep status | `workflow_steps.status` | `WorkflowGovernanceService` (+ planning create) | — |
| WorkflowStep progress | `workflow_steps.progress_percent` | `ProgressService` (cache) | **derived** from work orders |
| Execution commitment | `work_order_workflow_steps.execution_weight` | `WorkflowExecutionService` | — |
| WorkOrder status | `work_orders.status` | `PlanningUseCases` (create) / callers | gates progress |
| DailyReport | `daily_reports` row | `WorkflowExecutionService` | — |
| Approval | `approvals` row | `WorkflowGovernanceService` | — |
| Inspection / PunchItem | their rows | quality flow via repos | — |
| Blocker | `blockers` row | `WorkflowGovernanceService` | open/closed sets derived by analytics |
| BOQMapping | `boq_mappings` row | `WorkflowExecutionService` | — |
| Access grants | `project_memberships` rows | `ProjectAccessService` | — |
| Credentials/roles | `platform_users` rows | `UserAuthService` | — |

**Rule:** each authoritative field has exactly one writing service. Routers and
analytics never write domain truth.

---

## Derived-truth contracts

These values are **functions of stored rows** and are only as true as their last
computation. They must never be persisted-and-trusted as independent facts (the
one persisted exception, `progress_percent`, is explicitly a cache).

### Progress (`ProgressService`)

- **Contract:** `step.progress = Σ(execution_weight where WO.status=COMPLETED) /
  Σ(all linked execution_weight) × 100`, quantized to 2 decimals (`ROUND_HALF_UP`).
- Activity progress = unweighted mean of its steps; project progress = unweighted
  mean of its activities.
- **Truth caveat:** `progress_percent` on the row is a **cache** written by
  `persist_workflow_step_progress`. The live truth is the recomputation; the cache
  can be stale if work-order statuses changed without a recompute call.
- Missing inputs resolve to `0` (no step / no activity / no links → 0), never error.

### Runtime views (`RuntimeQueryService`)

- **Contract:** read-only composition of authoritative rows + freshly computed
  progress. Views carry **no independent truth** — they are snapshots assembled
  per request and never written back.

### Analytics (`operational_/decision_/coordination_intelligence`, adoption, etc.)

- **Contract:** deterministic, explainable heuristics over DB rows + JSONL.
- Each output carries `false_positive_notes` and uses tunable thresholds —
  signals are **interpretations**, not facts.
- Every builder accepts `db: Session | None` and returns `data_available: False`
  when the DB is missing → analytics never assert truth without the source.

---

## Concurrency truth contract (optimistic locking)

There is **no version column**. Truth-consistency under concurrent writes is
enforced by the `updated_at` timestamp acting as an optimistic token
(`repositories/optimistic.py`, applied in `BaseRepository.update`).

Contract:

1. A caller may pass `expected_updated_at` for the resource it intends to change.
2. Before writing, the repo reloads the row and compares `stored.updated_at` to
   `expected` (UTC-normalized, exact match).
3. Mismatch (or row gone) → `ConcurrencyConflictError` → HTTP `409` at the router.
4. On success, `touch_updated_at` advances `updated_at`, invalidating other
   in-flight tokens.

Cross-resource nuance: a `DailyReport` is created under the **work order's**
token (`expected_work_order_updated_at`) — the report's truth depends on the
parent's unchanged state, not its own.

If `expected_updated_at` is omitted, the check is skipped (last-write-wins). So
the contract is **opt-in per call**; concurrency safety is a caller responsibility.

---

## Representation truth contract (schemas)

- **ORM models are never returned over the API.** Routers always convert to
  Pydantic `*Read` schemas (`model_validate`). The wire representation is a
  contract distinct from the storage representation.
- This means: internal columns can exist without being exposed, and the API shape
  is a deliberate projection of truth, not the raw row.

---

## Transaction truth contract

- `BaseRepository` is **persistence-only**: `create`/`update`/`delete` call
  `flush` (+`refresh`) but **never commit**. "Callers own transaction
  commit/rollback" (repository docstring).
- Therefore the boundary of a "true, committed change" is the request/session
  scope above the repository — a service can stage multiple writes that become
  true atomically only when the owning session commits.
- `approve_workflow_step` relies on this: it creates an `Approval` **and** updates
  the step status within the same unit of work.

---

## Identity truth

- Domain primary keys are DB-generated UUIDs (`gen_random_uuid()`), so identity
  truth originates in PostgreSQL, not the application.
- Natural keys carry uniqueness truth: `projects.code`, `(project_id, code)` for
  WBS/Location/Activity, `(project_id, work_order_number)`, `(activity_instance_id,
  code)` for steps, and the junction uniqueness pairs. These are the
  business-identity contracts the DB guarantees.
- User attribution fields (`created_by`, `submitted_by`, `approved_by`,
  `reported_by`, `assigned_to`) are **soft** UUIDs with no FK — their truth is
  "who claimed to act," retained even if the user record changes.

---

## Truth-contract summary (the invariants)

1. **DB is authoritative; everything else is a projection.**
2. **One writer per authoritative field** (a specific service).
3. **Derived values (progress, views, analytics) are never independent truth.**
4. **`progress_percent` is a cache** — recomputation is the real value.
5. **Concurrency safety is opt-in** via `updated_at` tokens → `409` on conflict.
6. **API truth ≠ storage truth** — schemas mediate every response.
7. **Repositories never commit** — atomic truth is set at the session boundary.
8. **JSONL logs are observational**, safely discardable, never authoritative.
