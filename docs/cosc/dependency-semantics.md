# COSC — Dependency Semantics

> How concepts depend on each other at runtime, extracted from FK definitions,
> `ondelete` rules, service call paths, and progress arithmetic. This covers both
> **data dependencies** (FKs) and **operational dependencies** (one thing must
> happen / exist before another is meaningful).

## 1. Data dependency graph (foreign keys)

All FKs are `RESTRICT` unless noted. `RESTRICT` means a parent **cannot be
deleted** while children exist — the system is built to preserve operational
history.

```
Project (root)
├─ WBSItem            (project_id RESTRICT; parent_id self SET NULL)
├─ Location           (project_id RESTRICT; parent_id self SET NULL)
├─ BOQItem            (project_id RESTRICT)
├─ ActivityInstance   (project_id RESTRICT, wbs_item_id RESTRICT, location_id RESTRICT)
│   └─ WorkflowStep   (activity_instance_id RESTRICT; workflow_template_id RESTRICT nullable)
│       ├─ Approval        (workflow_step_id RESTRICT)
│       ├─ Inspection      (workflow_step_id RESTRICT)
│       │   └─ PunchItem   (workflow_step_id RESTRICT, inspection_id RESTRICT)
│       ├─ Blocker         (workflow_step_id RESTRICT)
│       ├─ BOQMapping      (workflow_step_id RESTRICT, boq_item_id RESTRICT)   [deletable]
│       └─ WorkOrderWorkflowStep (workflow_step_id CASCADE)                    [deletable]
├─ WorkOrder          (project_id RESTRICT)
│   ├─ WorkOrderWorkflowStep (work_order_id CASCADE)                           [deletable]
│   └─ DailyReport    (work_order_id RESTRICT)
└─ ProjectMembership  (project_id CASCADE)   [auth infra, not domain]

WorkflowStepTemplate  (referenced by WorkflowStep, owns nothing)
PlatformUser          (referenced by username only, no FK)
```

### Delete-rule semantics

| Rule | Where | Operational meaning |
|---|---|---|
| `RESTRICT` | All domain parent→child FKs | History is immutable; you cannot erase a project/step/work order that has operational data under it. |
| `CASCADE` | `WorkOrderWorkflowStep.work_order_id`, `project_memberships.project_id` | A work order's commitments die with it; membership grants die with the project. |
| `SET NULL` | `WBSItem.parent_id`, `Location.parent_id` | Removing a tree node re-roots its children instead of deleting them. |

The application reinforces this with `delete_policy.assert_delete_allowed`:
only `WorkOrderWorkflowStep` and `BOQMapping` may be deleted through repositories;
every other model raises on delete. So **data dependency is intentionally rigid**:
correction happens by adding/removing junction links, not by deleting core records.

## 2. The defining dependency: WBS × Location → ActivityInstance

An `ActivityInstance` requires **all three** of `Project`, `WBSItem`, `Location`,
and is unique per `(project_id, wbs_item_id, location_id)`. This encodes the core
operational rule:

> Real work = a unit of scope (**WBS**) performed at a place (**Location**),
> exactly once per intersection.

This is the semantic seam between planning and reality. Above it (WBS, Location,
BOQ) everything is intent. At and below it (ActivityInstance → WorkflowStep →
WorkOrder/Evidence/Quality) everything is execution.

## 3. The progress dependency chain

Progress is **commitment-based** and flows bottom-up (`ProgressService`):

```
WorkOrder.status == COMPLETED
        │ contributes execution_weight (via WorkOrderWorkflowStep)
        ▼
WorkflowStep.progress = Σ(completed WO weight) / Σ(all WO weight) × 100
        │ unweighted average
        ▼
ActivityInstance.progress = avg(child WorkflowStep progress)
        │ unweighted average
        ▼
Project.progress = avg(ActivityInstance progress)
```

Operational dependency facts:

- A step's progress depends on **work orders for the whole project**, filtered to
  links pointing at that step (`ProgressService.calculate_workflow_step_progress`
  iterates project work orders and their links).
- A step with **no** work-order links has progress `0` (zero denominator → 0).
- Roll-ups are **unweighted averages** at activity and project level — a small
  step counts the same as a large one. `planned_weight` exists on the step but is
  **not** used by the current roll-up.
- `progress_percent` stored on `WorkflowStep` is a cache of this computation, not
  an input to it.

## 4. Operational (event-order) dependencies

These are sequencing dependencies enforced or assumed by services, independent of
FKs.

| Dependent action | Depends on | Enforced by |
|---|---|---|
| Assign work order to step | both `WorkOrder` and `WorkflowStep` must exist; link must not already exist | `WorkflowExecutionService.assign_work_order_to_workflow_step` (existence + duplicate guard) |
| Submit daily report | parent `WorkOrder` exists and unchanged since `expected_work_order_updated_at` | `create_daily_report` (existence + optimistic check) |
| Link BOQ item | `WorkflowStep` exists | `link_boq_item` |
| Pass inspection | step status == `INSPECTION_PENDING` | `mark_inspection_passed` |
| Approve step | step exists; no duplicate `APPROVED` of same type | `approve_workflow_step` |
| Step progress > 0 | at least one **completed** work order linked | `ProgressService` |
| Resolve blocker | blocker exists | `resolve_blocker` |

Note what is **not** enforced: there is no dependency between steps (no
predecessor/successor graph), no rule that inspection precedes approval in code
(governance can approve from any state, dup-guarded), and no rule that a blocker
freezes progress. These are conventions, not constraints.

## 5. Access-control dependency

Every project-scoped operation depends on a membership check before it runs
(`ProjectAccessService.ensure_project_access`), resolved through the chain:

```
WorkOrder/Activity/Step  ──get_*_project_id──▶  Project  ──membership──▶  allow/deny
```

- Admin → `get_accessible_project_ids` returns `None` = all projects (no filter).
- Non-admin → access depends on rows in `project_memberships`.
- Side-effect grants: creating a project grants the creator + all investors;
  assigning a work order grants the operational team (supervisors + workers);
  submitting a report grants the submitter. So **membership is partly derived from
  participation**, not only from explicit admin grants.

## 6. Service dependency layering

Runtime depends downward only; nothing lower calls upward.

```
Router (planning_router / runtime_router / analytics_router)
   ▼ depends on
Application use cases (PlanningUseCases / RuntimeUseCases)
   ▼ depends on
Services (Progress / WorkflowExecution / WorkflowGovernance / RuntimeQuery)
   ▼ depends on
Repositories (BaseRepository + per-entity)
   ▼ depends on
ORM models  ──▶  PostgreSQL
```

- `RuntimeQueryService` and `RuntimeUseCases` depend on `ProgressService` for
  derived numbers but never persist.
- Analytics services depend **only** on ORM models + repositories + the JSONL
  stores; they are read-side leaves with no write dependents.
- `ProjectAccessService` depends on `ProjectMembershipRepository` and
  `UserAuthService` (for role-based bulk grants).

## 7. Dependency inversion points

- `WorkflowStep.workflow_template_id` is **nullable** — a step can execute without
  knowledge (template). Knowledge is an optional dependency.
- `created_by`, `submitted_by`, `approved_by`, `reported_by`, `assigned_to` are
  bare `UUID` columns with **no FK** to `platform_users`. User attribution is a
  soft dependency (kept even if the user record changes/disappears).
- Analytics degrade gracefully: every analytics builder accepts `db: Session | None`
  and returns a `data_available: False` shell when the DB is absent — analytics
  depend on the DB but never hard-fail the request.

## 8. What has no dependents (safe to evolve)

- `WorkflowStepTemplate` knowledge fields, `DailyReport` evidence fields,
  `PunchItem` remediation fields, and all JSONL analytics outputs are **leaf**
  data — nothing computes on them as authoritative inputs to progress or
  governance. They are observed, not depended upon.
