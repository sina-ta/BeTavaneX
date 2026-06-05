# COSC — Lifecycle Semantics

> Status states and transitions as they exist **today** in the BetavanX backend.
> States come from the `CheckConstraint` definitions on the ORM models;
> transitions come from the services and routers that actually perform them.
>
> Important: most status columns are **free-set strings** constrained only by a
> CHECK list. The database enforces the *set* of legal values, not the *order* of
> transitions. Only `WorkflowStep` (and `Blocker`/`Approval` via dedicated
> methods) has transition logic enforced in code. Everywhere else, ordering is a
> convention applied by callers, not a guard.

## Legend

- **Enforced** — a service method validates the source state before transitioning.
- **Set-only** — the value must be in the CHECK list, but any value can be set
  from any state (no ordering guard in code).
- **Default** — the `server_default` the row is born with.

---

## Project

- States: `DRAFT`, `ACTIVE`, `ON_HOLD`, `COMPLETED`, `CANCELLED`
- Default: `ACTIVE`
- Created by: `PlanningUseCases.create_project` (default `ACTIVE`, or caller-supplied).
- Transition enforcement: **Set-only**. No service guards project status order.
- Operational meaning of terminal states: `COMPLETED`/`CANCELLED` are convention
  terminal; nothing in code blocks further edits based on them.

## WBSItem

- States: `ACTIVE`, `COMPLETED`, `CANCELLED` — Default `ACTIVE`
- Transition enforcement: **Set-only**.
- Note: `parent_id` FK is `SET NULL` — deleting a parent orphans children to root,
  it does not cascade-delete the subtree.

## Location

- States: `ACTIVE`, `CLOSED` — Default `ACTIVE`
- Transition enforcement: **Set-only**.
- Same `SET NULL` parent behavior as WBS.

## BOQItem

- States: `DRAFT`, `APPROVED`, `ACTIVE`, `CLOSED` — Default `ACTIVE`
- Transition enforcement: **Set-only**.
- Note: created directly as `ACTIVE` by default; the `DRAFT → APPROVED` flow is
  available as values but not driven by any current service.

## ActivityInstance

- States: `ACTIVE`, `COMPLETED`, `CANCELLED` — Default `ACTIVE`
- Transition enforcement: **Set-only**.
- Progress is **not** stored here; completion is a header flag, while real
  progress is derived from child workflow steps (see `ProgressService`).

---

## WorkflowStep (the governed lifecycle)

This is the only entity with a meaningful, code-enforced state machine.

- States: `PLANNED`, `IN_PROGRESS`, `COMPLETED`, `INSPECTION_PENDING`,
  `INSPECTION_FAILED`, `REWORK_REQUIRED`, `APPROVED`
- `status` has **no** `server_default` — it is set explicitly at creation by
  `PlanningUseCases.create_workflow_step`.
- Additional state: `ready: bool` (default `false`) and `progress_percent`
  (0–100, default 0, derived/cached).

### Enforced transitions (`WorkflowGovernanceService`)

| Method | Precondition (enforced) | Result |
|---|---|---|
| `mark_inspection_passed` | status **must be** `INSPECTION_PENDING` | → `APPROVED` |
| `mark_inspection_failed` | none | → `INSPECTION_FAILED` |
| `require_rework` | none | → `REWORK_REQUIRED` |
| `approve_workflow_step` | step exists; no existing `APPROVED` approval of same type | creates `Approval(APPROVED)` **and** sets step → `APPROVED` |

Only `mark_inspection_passed` guards its source state. The others are unguarded
setters that still produce valid CHECK values.

### Transition diagram (as actually reachable in code)

```
                         create_workflow_step(status=<caller>)
                                       |
            +--------------------------+--------------------------+
            v                                                     v
        PLANNED / IN_PROGRESS / COMPLETED ...            (any starting status)
            |
            |  (field/quality flow sets status to INSPECTION_PENDING — set-only)
            v
     INSPECTION_PENDING --mark_inspection_passed--> APPROVED
            |                                          ^
            |--mark_inspection_failed--> INSPECTION_FAILED
                                              |
                                              v (set-only)
                                       REWORK_REQUIRED
            approve_workflow_step (from any state, dup-guarded) --> APPROVED
```

### Notes on reality

- `progress_percent` is recomputed and persisted by
  `ProgressService.persist_workflow_step_progress`; it is a cache, not an
  independent lifecycle.
- `ready` is a stored boolean filter flag; nothing in the current services
  computes or flips it automatically (it is set at creation / via planning).
- There is no automatic `PLANNED → IN_PROGRESS` driver in code; intermediate
  movement is performed by callers setting status.

---

## WorkOrder

- States: `CREATED`, `ASSIGNED`, `IN_PROGRESS`, `COMPLETED`, `CANCELLED`
- Default: `CREATED`
- Transition enforcement: **Set-only**.
- **Operationally critical state**: `COMPLETED`. `ProgressService` only counts a
  work order's `execution_weight` as *completed weight* when
  `work_order.status == "COMPLETED"`. This single status value is the hinge of all
  progress arithmetic.
- `CREATED`/`ASSIGNED` are treated by analytics as "inactive" states when stale
  (see `event-taxonomy.md`).

## WorkOrderWorkflowStep (junction)

- No status. Lifecycle is **exists / removed**.
- Created by assignment; duplicate `(work_order, step)` is blocked and raises an
  operational alert. Removable via `remove_work_order_assignment` (delete-allowed).

## DailyReport

- States: `DRAFT`, `SUBMITTED`, `REVIEWED`, `ACCEPTED`, `REJECTED`
- Default: `DRAFT`
- Created by `create_daily_report` with caller-supplied status (default `DRAFT`).
- Transition enforcement: **Set-only**.
- Creation is guarded by optimistic concurrency against the parent **work order's**
  `updated_at` (not the report's own), preventing reports against a concurrently
  changed work order.

---

## Approval

- States: `PENDING`, `UNDER_REVIEW`, `APPROVED`, `REJECTED`
- No default; `status` is set at creation.
- The live path (`approve_workflow_step`) creates approvals directly as `APPROVED`.
  `PENDING`/`UNDER_REVIEW` values exist and are consumed by analytics (pending
  approval detection), but the current write path does not create them.
- Enforcement: duplicate `APPROVED` of the same `approval_type` on a step is
  blocked; the step is moved to `APPROVED` in the same operation with an optimistic
  check on the step.

## Inspection

- States: `CREATED`, `SCHEDULED`, `IN_PROGRESS`, `PASSED`, `FAILED`
- `result`: `PASS` | `FAIL` (required, CHECK-constrained)
- Transition enforcement: **Set-only**. Inspection status/result are recorded;
  the step's reaction to a pass/fail is performed separately through governance
  (`mark_inspection_passed` / `mark_inspection_failed`).

## PunchItem

- States: `OPEN`, `ASSIGNED`, `IN_PROGRESS`, `RESOLVED`, `VERIFIED`, `CLOSED`, `REOPENED`
- Severity: `LOW`, `MEDIUM`, `HIGH`, `CRITICAL`
- Transition enforcement: **Set-only**. `closed_at` is a separate timestamp the
  caller sets on closure.

## Blocker

- States: `OPEN`, `ACKNOWLEDGED`, `MITIGATION_IN_PROGRESS`, `RESOLVED`, `CLOSED`, `REOPENED`
- Type: `WEATHER`, `EQUIPMENT`, `MATERIAL`, `WORKFORCE`, `SITE_CONDITION`, `EXTERNAL`
- Severity: `LOW`, `MEDIUM`, `HIGH`, `CRITICAL`
- Created `OPEN` by `add_blocker`.
- Enforced transition: `resolve_blocker` sets status → `RESOLVED` and stamps
  `resolved_date` / `resolution_notes`.
- Analytics treat `{OPEN, ACKNOWLEDGED, MITIGATION_IN_PROGRESS, REOPENED}` as the
  "open" set; `RESOLVED`/`CLOSED` are effectively closed.

## WorkflowStepTemplate

- States: `ACTIVE`, `ARCHIVED` — Default `ACTIVE`
- Transition enforcement: **Set-only**. Archiving is a soft-retire of reference
  knowledge; existing steps keep their reference.

---

## Cross-cutting lifecycle rules

### Timestamps as lifecycle signal

Every domain table has `created_at` and (except junctions) `updated_at` with DB
defaults. `updated_at` is the **optimistic-lock token** and is bumped on every
`BaseRepository.update` via `touch_updated_at`. Analytics interpret a stale
`updated_at` (relative to `OPS_STALL_DAYS` / `OPS_APPROVAL_DELAY_DAYS`) as
stagnation — so `updated_at` carries lifecycle meaning beyond bookkeeping.

### Deletion as a lifecycle boundary

There is no soft-delete state. Records are not deleted except the two junction
models (`WorkOrderWorkflowStep`, `BOQMapping`). All other models use `RESTRICT`
FKs and are blocked from deletion by `delete_policy.assert_delete_allowed`.
Lifecycle therefore ends in a **terminal status**, not in row removal.

### Who can drive each lifecycle

| Lifecycle | Driven by | Allowed roles |
|---|---|---|
| Planning entities (create) | `PlanningUseCases` → planning router | `admin`, `supervisor` |
| WorkOrder assignment | `WorkflowExecutionService` | `admin`, `supervisor` |
| DailyReport submission | `WorkflowExecutionService` | `admin`, `supervisor`, `worker` |
| Approval / step approval | `WorkflowGovernanceService` | `admin`, `supervisor` |
| Blocker open/resolve | `WorkflowGovernanceService` | (recorded against step) |
| Progress recompute | `ProgressService` | system (read/compute) |

### Summary of enforcement reality

- **Strongly enforced**: duplicate-assignment guard, duplicate-approval guard,
  `INSPECTION_PENDING → APPROVED` precondition, optimistic `updated_at` checks,
  delete restriction.
- **Convention only (set-only)**: nearly all other status orderings. The system
  trusts the caller/role to apply transitions in sensible order; the DB only
  guarantees the value is in the legal set.
