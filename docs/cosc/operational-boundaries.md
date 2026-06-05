# COSC — Operational Boundaries

> The lines the system draws between layers, responsibilities, and authority.
> These are the boundaries that already exist in code (enforced by class
> responsibilities, role policies, FK rules, and docstring contracts). Respecting
> them is what keeps BetavanX's semantics stable.

## 1. Layer responsibility boundaries

Each layer has a single job and explicitly refuses the others (stated in module
docstrings and enforced by what each class is wired to call).

```
HTTP boundary
  └─ Routers (planning/runtime/analytics/pilot)
        responsibility: validate input (Pydantic), authorize, delegate, map to Read schemas
        forbidden: business logic, calculations, repository access, returning ORM
  └─ Application use cases (PlanningUseCases / RuntimeUseCases)
        responsibility: orchestrate services
        forbidden: ORM construction beyond entity assembly, repository internals, formulas
  └─ Services (Progress / WorkflowExecution / WorkflowGovernance / RuntimeQuery)
        responsibility: the one operation family they own
        forbidden: crossing into each other's concern (see §2)
  └─ Repositories (BaseRepository + per-entity)
        responsibility: persistence only (flush/refresh)
        forbidden: committing transactions, business rules
  └─ ORM models / PostgreSQL
        responsibility: hold authoritative state + constraints
```

Boundary contract phrases taken directly from the code:

- Planning use cases: *"thin persistence facade … no business rules, no
  workflow/progress/readiness calculation, no planning intelligence."*
- `RuntimeUseCases`: *"Coordinates runtime services; no ORM, repository, or formula
  logic."*
- `RuntimeQueryService`: *"Read-only runtime views; no persistence or workflow side
  effects."*
- `WorkflowExecutionService`: *"Persistence-only runtime operations; no progress or
  workflow calculation."*
- `BaseRepository`: *"Persistence-only data access; callers own transaction
  commit/rollback."*

## 2. Service-responsibility boundaries (separation of powers)

The four runtime services are deliberately non-overlapping:

| Service | Owns | Must NOT do |
|---|---|---|
| `ProgressService` | progress arithmetic (step/activity/project) | change status, persist anything except the progress cache |
| `WorkflowExecutionService` | links, reports, BOQ mappings (persistence) | compute progress, change workflow status |
| `WorkflowGovernanceService` | status transitions, approvals, blocker lifecycle | compute progress, do reporting/execution |
| `RuntimeQueryService` | read-only composition of views | write anything, cause side effects |

This is the central semantic boundary: **execution, governance, measurement, and
reading are four separate authorities.** A single field action that touches more
than one is composed at the use-case layer, not collapsed into one service.

## 3. The plan / reality boundary

The hardest semantic line in the domain:

```
Intent (Planning)                 |  Reality (Execution/Evidence/Quality)
Project, WBS, Location, BOQItem    |  ActivityInstance, WorkflowStep,
                                   |  WorkOrder, DailyReport, Inspection,
                                   |  Approval, PunchItem, Blocker, BOQMapping
```

`ActivityInstance` sits exactly on the seam — it is created as planning intent but
is the first place reality is recorded. Above the line, records describe what
should happen; below it, records describe what did. Progress only flows from the
reality side (completed work orders), never from planned values.

## 4. Authority (role) boundaries

Enforced at the router by `role_policy` dependencies:

| Operation class | Allowed roles | Boundary meaning |
|---|---|---|
| Planning creates | `admin`, `supervisor` | only planners shape scope |
| Work-order assignment | `admin`, `supervisor` | only supervisors commit field work |
| Daily report submission | `admin`, `supervisor`, `worker` | field actors capture evidence |
| Workflow approval / governance | `admin`, `supervisor` | only supervisors grant authority |
| Runtime reads | all authenticated roles incl. `investor` | everyone may observe |

`investor` is a **read-only boundary** — present in every reader policy, absent
from every mutator policy.

## 5. Project access boundary (tenancy)

Every project-scoped operation passes through `ProjectAccessService.ensure_project_access`
before acting:

- **Admins bypass** membership (access all projects) — the one boundary exception.
- Non-admins are confined to projects in `project_memberships`.
- The boundary is resolved by walking the resource up to its project
  (`get_*_project_id`) and checking membership; cross-project access is impossible
  for non-admins even with a valid resource id.
- Membership can be **earned by participation** (creating a project, being on the
  assigned operational team, submitting a report) — the boundary expands as people
  actually work, not only via explicit grants.

## 6. Mutation boundary (deletion & history)

- **Default = no deletion.** `delete_policy.assert_delete_allowed` blocks deletes
  for every model except `WorkOrderWorkflowStep` and `BOQMapping`.
- All domain parent→child FKs are `RESTRICT` → operational history cannot be erased
  by removing parents.
- Correction happens **inside** the boundary by adding/removing the two allowed
  junction links, never by destroying core records.
- Consequence: lifecycles end in terminal **status**, not in row removal (see
  `lifecycle-semantics.md`).

## 7. Concurrency boundary

- The unit of safe change is the row guarded by its `updated_at` token.
- Conflicts surface as `409` at the HTTP boundary and as `conflict`-category audit
  records — the boundary between "my change is valid" and "the world moved under
  me" is explicit and observable.
- Transaction atomicity boundary is the **session above the repository**;
  repositories never commit, so a multi-write operation is atomic only within its
  owning unit of work.

## 8. Knowledge / instance boundary

- `WorkflowStepTemplate` (knowledge) is referenced, never owned, by `WorkflowStep`
  (instance), and the link is **nullable**.
- Boundary meaning: standard methods evolve independently of live execution; a
  running step is not invalidated when its template changes or is archived.

## 9. Analytics boundary (observation, never control)

This is the boundary the COSC phase most needs to protect:

- Analytics services are **read-only leaves**. They consume rows + JSONL and emit
  signals/scores. They write **nothing** to the domain.
- Signals are **advisory**: severity `info/warning/critical` triggers **no
  automatic action** — no auto-approval, no auto-assignment, no status change.
  Coordination intelligence states this explicitly: *"does not auto-assign or
  auto-approve."*
- Analytics **degrade, never block**: missing DB → `data_available: False` shell;
  query errors are swallowed into a safe summary. The request path is never held
  hostage by interpretation.
- Thresholds are environment-tunable heuristics with declared `false_positive_notes`
  — the boundary between "signal" and "fact" is documented in the output itself.

## 10. Persistence-shape boundary

- Domain data lives in **relational tables**; flexible/auxiliary data lives in
  **JSONB columns** (`workflow_step_templates` requirement lists,
  `daily_reports.evidence_metadata`) — not new tables.
- Observational data lives in **JSONL files**, deliberately outside the relational
  domain.
- This three-way split (tables / JSONB / JSONL) is the existing boundary for "what
  is core state vs. flexible attributes vs. observation."

---

## Boundary integrity checklist (for future changes)

Any change should preserve these existing lines:

1. Routers stay thin; no logic or ORM leakage.
2. Each service keeps its single responsibility; compose at the use-case layer.
3. Progress stays derived from completed work-order weights only.
4. Writes go through the one owning service per field; reads never write.
5. Deletion stays restricted to the two junctions.
6. Project access is checked for every project-scoped operation; only admins bypass.
7. Analytics remain read-only, advisory, and degrade gracefully.
8. PostgreSQL remains the sole source of authoritative truth.
