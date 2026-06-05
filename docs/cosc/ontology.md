# COSC — Ontology

> Construction Operational Semantic Core (COSC). This document extracts the
> operational meaning of every core concept that already exists in the BetavanX
> Phase 1 backend. It describes what the system **actually does today**, not a
> target design. Nothing here introduces new entities or behavior.

## How to read this

Every concept is an existing ORM model, service, or runtime construct. Each
entry defines:

- **Purpose** — why the concept exists operationally.
- **Operational meaning** — what it represents on a real construction project.
- **Authority** — who/what is allowed to change it (role + layer).
- **Lifecycle** — its status states (detailed in `lifecycle-semantics.md`).
- **Mutability** — how it changes after creation.
- **Source of truth** — where its authoritative value lives.
- **Relationship semantics** — how it binds to other concepts.
- **Operational boundary** — what it must not do (detailed in `operational-boundaries.md`).
- **Execution role** — its function during runtime.

## Layer map (from model docstrings)

The codebase already tags each model with a layer in its module docstring:

| Layer | Concepts |
|---|---|
| Planning | `Project`, `WBSItem`, `Location` |
| Financial / Planning | `BOQItem` |
| Construction Reality | `ActivityInstance` |
| Execution Knowledge | `WorkflowStepTemplate` |
| Execution Reality | `WorkflowStep` |
| Execution Coordination | `WorkOrder`, `WorkOrderWorkflowStep` |
| Execution Evidence | `DailyReport` |
| Quality | `Inspection`, `Approval`, `PunchItem` |
| Operational Constraint | `Blocker` |
| Financial Integration | `BOQMapping` |
| Auth / IAM (not a domain entity) | `PlatformUser`, `ProjectMembership` |

Two semantic axes run through the system:

1. **Plan vs. Reality** — Planning concepts describe intent; Execution Reality
   and Evidence concepts describe what actually happened.
2. **Knowledge vs. Instance** — `WorkflowStepTemplate` is reusable knowledge; a
   `WorkflowStep` is one concrete application of it on one `ActivityInstance`.

---

## Planning Layer

### Project

- **Purpose**: Top-level container and scoping root for all operational data.
- **Operational meaning**: A single construction project (contract/site).
- **Authority**: Created/updated by planning actors (`admin`, `supervisor`).
- **Lifecycle**: `DRAFT → ACTIVE → ON_HOLD → COMPLETED → CANCELLED` (default `ACTIVE`).
- **Mutability**: Mutable header (name, status, planned dates). `code` is unique and stable.
- **Source of truth**: `projects` table.
- **Relationship semantics**: Parent of `WBSItem`, `Location`, `BOQItem`,
  `ActivityInstance` (all via `RESTRICT` FK). Access is scoped through
  `ProjectMembership`.
- **Operational boundary**: The unit of access control. Every runtime read/write
  is authorized against project membership.
- **Execution role**: The aggregate root. Progress, dashboards, and all
  analytics are computed per project.

### WBSItem (Work Breakdown Structure item)

- **Purpose**: The *what* dimension of scope — hierarchical decomposition of work.
- **Operational meaning**: A node in the project's work breakdown (e.g. "Foundations → Footings").
- **Authority**: Planning actors.
- **Lifecycle**: `ACTIVE → COMPLETED → CANCELLED`.
- **Mutability**: Mutable; self-referential tree via `parent_id` (`SET NULL` on parent delete).
- **Source of truth**: `wbs_items` table; `(project_id, code)` unique.
- **Relationship semantics**: Belongs to one `Project`; has a parent/children
  tree; combines with `Location` to define `ActivityInstance`.
- **Operational boundary**: Structural classification only — carries no progress or execution state.
- **Execution role**: One of the two coordinates that locate an activity.

### Location

- **Purpose**: The *where* dimension of scope.
- **Operational meaning**: A physical/spatial node (zone, floor, axis, room).
- **Authority**: Planning actors.
- **Lifecycle**: `ACTIVE → CLOSED`.
- **Mutability**: Mutable; self-referential tree via `parent_id` (`SET NULL`).
- **Source of truth**: `locations` table; `(project_id, code)` unique.
- **Relationship semantics**: Belongs to one `Project`; parent/children tree;
  combines with `WBSItem` to define `ActivityInstance`.
- **Operational boundary**: Spatial classification only — no execution state.
- **Execution role**: The second coordinate that locates an activity.

### BOQItem (Bill of Quantities item)

- **Purpose**: The contractual/financial unit of measured work.
- **Operational meaning**: A priced line item (quantity × rate = planned cost).
- **Authority**: Planning actors.
- **Lifecycle**: `DRAFT → APPROVED → ACTIVE → CLOSED`.
- **Mutability**: Mutable header; constrained (`quantity > 0`, `rate >= 0`); default currency `IRR`.
- **Source of truth**: `boq_items` table.
- **Relationship semantics**: Belongs to one `Project`; consumed by `WorkflowStep`
  through `BOQMapping`.
- **Operational boundary**: Holds planned cost/quantity; it is **not** earned-value or actuals.
- **Execution role**: The financial reference that execution allocates against.

---

## Construction Reality Layer

### ActivityInstance

- **Purpose**: The concrete unit of construction work — where plan becomes reality.
- **Operational meaning**: "This specific work, in this WBS scope, at this location."
- **Authority**: Planning actors create it; status reflects construction reality.
- **Lifecycle**: `ACTIVE → COMPLETED → CANCELLED`.
- **Mutability**: Mutable header and planned dates/duration.
- **Source of truth**: `activity_instances` table. Uniqueness is enforced twice:
  `(project_id, code)` and `(project_id, wbs_item_id, location_id)` — i.e. one
  activity per WBS×Location intersection.
- **Relationship semantics**: Requires `Project`, `WBSItem`, and `Location`
  (all `RESTRICT`). Owns `WorkflowStep`s.
- **Operational boundary**: The intersection of *what* (WBS) and *where* (Location).
  It does not store its own progress; progress is derived from its steps.
- **Execution role**: The container under which execution actually happens; the
  mid-level rollup point for progress.

---

## Execution Knowledge Layer

### WorkflowStepTemplate

- **Purpose**: Reusable execution knowledge — the standard method for a step type.
- **Operational meaning**: A method statement library entry: how to do a step,
  what safety, permits, documents, resources, and inspections it needs.
- **Authority**: Maintained as reference data; referenced (not owned) by steps.
- **Lifecycle**: `ACTIVE → ARCHIVED`.
- **Mutability**: Mutable knowledge fields (free text + JSONB requirement lists).
- **Source of truth**: `workflow_step_templates` table; `code` unique.
- **Relationship semantics**: One template is referenced by many `WorkflowStep`s
  (`workflow_template_id`, nullable, `RESTRICT`).
- **Operational boundary**: Pure knowledge/reference. Holds no progress, status
  transitions, or project linkage.
- **Execution role**: Supplies the "how-to" that a concrete step is executed against.

---

## Execution Reality Layer

### WorkflowStep

- **Purpose**: The atomic, governable unit of execution and progress.
- **Operational meaning**: One executable step of an activity (e.g. "rebar fixing"),
  with status, readiness, and progress.
- **Authority**: Created by planning actors; status governed by
  `WorkflowGovernanceService`; progress computed by `ProgressService`.
- **Lifecycle**: `PLANNED → IN_PROGRESS → COMPLETED → INSPECTION_PENDING →
  INSPECTION_FAILED → REWORK_REQUIRED → APPROVED` (see lifecycle doc for the real
  governed transitions).
- **Mutability**: `status`, `ready` (bool), `progress_percent` (0–100, derived),
  `planned_weight`, planned/actual dates. `(activity_instance_id, code)` unique.
- **Source of truth**: `workflow_steps` table. `progress_percent` is the
  *persisted cache* of a value the `ProgressService` derives from work orders.
- **Relationship semantics**: Belongs to one `ActivityInstance`; optionally
  references a `WorkflowStepTemplate`; is the anchor for `Approval`, `Inspection`,
  `PunchItem`, `Blocker`, `BOQMapping`, and `WorkOrderWorkflowStep`.
- **Operational boundary**: The lowest level at which governance and progress
  exist. It does not compute its own progress; it is the target of commitments.
- **Execution role**: The central runtime entity — almost every operational
  signal hangs off a workflow step.

---

## Execution Coordination Layer

### WorkOrder

- **Purpose**: The daily/field unit of committed and executed work.
- **Operational meaning**: An instruction to perform work on a planned date,
  later marked completed when the field work is done.
- **Authority**: Created by planning actors; assigned by work-order assigners
  (`admin`, `supervisor`).
- **Lifecycle**: `CREATED → ASSIGNED → IN_PROGRESS → COMPLETED → CANCELLED`.
- **Mutability**: Mutable header, `planned_date`, `status`; `(project_id, work_order_number)` unique.
- **Source of truth**: `work_orders` table.
- **Relationship semantics**: Belongs to one `Project`; links to `WorkflowStep`s
  through `WorkOrderWorkflowStep`; owns `DailyReport`s. Its `status == COMPLETED`
  is what makes its committed weight count as progress.
- **Operational boundary**: Coordinates execution; it is the **commitment carrier**,
  not the step itself.
- **Execution role**: Progress is driven by completed work orders' execution weights.

### WorkOrderWorkflowStep (junction)

- **Purpose**: The commitment link between a work order and a workflow step.
- **Operational meaning**: "This work order contributes this much weight toward
  this step."
- **Authority**: `WorkflowExecutionService.assign_work_order_to_workflow_step`.
- **Lifecycle**: No status; exists or is removed.
- **Mutability**: Effectively immutable after creation; **deletable** (one of two
  deletable models). `execution_weight` constrained `> 0 and <= 100`.
- **Source of truth**: `work_order_workflow_steps` table; `(work_order_id, workflow_step_id)` unique.
- **Relationship semantics**: `CASCADE` from its `WorkOrder`. Carries `execution_weight`.
- **Operational boundary**: The only place execution weight lives; it is the
  numerator/denominator basis of step progress.
- **Execution role**: Converts work-order completion into measurable step progress.

---

## Execution Evidence Layer

### DailyReport

- **Purpose**: The field record of what happened against a work order on a day.
- **Operational meaning**: Daily site report — execution notes, issues, delays,
  weather, manpower/equipment/material counts, evidence metadata.
- **Authority**: Submitted by daily-report submitters (`admin`, `supervisor`, `worker`).
- **Lifecycle**: `DRAFT → SUBMITTED → REVIEWED → ACCEPTED → REJECTED`.
- **Mutability**: Created via `WorkflowExecutionService.create_daily_report` under
  optimistic check against the parent work order's `updated_at`.
- **Source of truth**: `daily_reports` table.
- **Relationship semantics**: Belongs to one `WorkOrder` (`RESTRICT`).
- **Operational boundary**: Evidence only. It does **not** move progress or step
  status; reported counts are descriptive, not authoritative resource ledgers.
- **Execution role**: Primary field-feedback signal; its frequency feeds health
  and coordination analytics.

---

## Quality Layer

### Inspection

- **Purpose**: Quality control event against a workflow step.
- **Operational meaning**: A recorded inspection with a pass/fail result.
- **Authority**: Quality/supervisory roles (recorded against a step).
- **Lifecycle**: `CREATED → SCHEDULED → IN_PROGRESS → PASSED → FAILED`; `result ∈ {PASS, FAIL}`.
- **Mutability**: Mutable status/result/notes.
- **Source of truth**: `inspections` table.
- **Relationship semantics**: Belongs to one `WorkflowStep` (`RESTRICT`); owns `PunchItem`s.
- **Operational boundary**: Records quality outcome; it does not itself flip step
  status — governance does that.
- **Execution role**: The quality gate evidence that precedes approval.

### Approval

- **Purpose**: The formal sign-off authorizing a step as accepted.
- **Operational meaning**: A governance decision ("FINAL approval granted").
- **Authority**: Workflow approvers (`admin`, `supervisor`) via
  `WorkflowGovernanceService.approve_workflow_step`.
- **Lifecycle**: `PENDING → UNDER_REVIEW → APPROVED → REJECTED`. The current
  approve path creates records directly in `APPROVED`.
- **Mutability**: Created with decision fields; duplicate `APPROVED` of the same
  `approval_type` is blocked.
- **Source of truth**: `approvals` table.
- **Relationship semantics**: Belongs to one `WorkflowStep` (`RESTRICT`).
  Creating an `APPROVED` approval also sets the step status to `APPROVED`.
- **Operational boundary**: The authoritative governance record; only governance
  may create it.
- **Execution role**: Closes the governance loop for a step.

### PunchItem

- **Purpose**: A tracked defect/snag raised from an inspection.
- **Operational meaning**: A remediation item ("fix this") with severity and owner.
- **Authority**: Quality/supervisory roles.
- **Lifecycle**: `OPEN → ASSIGNED → IN_PROGRESS → RESOLVED → VERIFIED → CLOSED → REOPENED`.
- **Mutability**: Mutable status/assignment/resolution; `severity ∈ {LOW, MEDIUM, HIGH, CRITICAL}`.
- **Source of truth**: `punch_items` table.
- **Relationship semantics**: Belongs to one `WorkflowStep` and one `Inspection` (both `RESTRICT`).
- **Operational boundary**: Defect tracking; does not block progress arithmetic directly.
- **Execution role**: Quality remediation trail.

---

## Operational Constraint Layer

### Blocker

- **Purpose**: A recorded impediment to executing a workflow step.
- **Operational meaning**: Something stopping work — weather, equipment, material,
  workforce, site condition, or external cause.
- **Authority**: Reported against a step; resolved via
  `WorkflowGovernanceService.resolve_blocker`.
- **Lifecycle**: `OPEN → ACKNOWLEDGED → MITIGATION_IN_PROGRESS → RESOLVED → CLOSED → REOPENED`.
- **Mutability**: Mutable status/resolution; `blocker_type` and `severity` constrained.
- **Source of truth**: `blockers` table.
- **Relationship semantics**: Belongs to one `WorkflowStep` (`RESTRICT`).
- **Operational boundary**: A constraint signal; it does **not** automatically
  change step status. Its impact is interpreted by analytics, not enforced.
- **Execution role**: Primary risk/impediment signal feeding health, decision
  support, and coordination intelligence.

---

## Financial Integration Layer

### BOQMapping (junction)

- **Purpose**: Allocates a BOQ item's quantity/cost to a workflow step.
- **Operational meaning**: "This step consumes this much of this BOQ line."
- **Authority**: `WorkflowExecutionService.link_boq_item` / `unlink_boq_item`.
- **Lifecycle**: No status; exists or is removed.
- **Mutability**: **Deletable** (second of two deletable models);
  `allocated_quantity > 0`, `allocated_cost >= 0`, optional `allocation_percentage` 0–100.
- **Source of truth**: `boq_mappings` table; `(workflow_step_id, boq_item_id)` unique.
- **Relationship semantics**: Joins one `WorkflowStep` to one `BOQItem` (both `RESTRICT`).
- **Operational boundary**: Cost/quantity allocation only; not actual spend or earned value.
- **Execution role**: Bridges execution and finance; basis for future cost rollups.

---

## Auth / IAM (infrastructure, not domain)

These exist to scope access and are explicitly **not** planning/runtime domain
entities (per their module docstrings).

### PlatformUser

- **Purpose**: Persisted credential + role for pilot users.
- **Operational meaning**: A login (`username`, `role`, `hashed_password`, `disabled`).
- **Authority**: IAM/seed; not part of project domain data.
- **Source of truth**: `platform_users` table; `username` is the primary key.
- **Relationship semantics**: Referenced by `ProjectMembership` by username (no FK).
- **Execution role**: Supplies role for route-level authorization and audit attribution.

### ProjectMembership

- **Purpose**: Scopes which non-admin users can access which projects.
- **Operational meaning**: A grant ("user X may see project Y").
- **Authority**: `ProjectAccessService`.
- **Source of truth**: `project_memberships` table; `(username, project_id)` unique;
  `CASCADE` from `Project`.
- **Relationship semantics**: Admins bypass membership entirely (access all projects).
- **Execution role**: The access-control filter applied to every project-scoped read/write.

---

## Roles (operational actors)

Defined in auth and mapped to operations by `role_policy`:

| Role | Can do |
|---|---|
| `admin` | Everything; bypasses project membership |
| `supervisor` | Planning creates, work-order assignment, daily reports, approvals |
| `worker` | Daily reports; runtime reads |
| `investor` | Runtime reads only; auto-granted membership on new projects |

---

## Derived (non-stored) concepts

These are **computed at runtime** and have no table. They are authoritative only
as functions of stored data, never as independent records.

- **Step / Activity / Project progress** — `ProgressService` (commitment-based).
- **Runtime views** — `RuntimeQueryService` (read-only composition).
- **Operational intelligence / health band** — `operational_intelligence_service`.
- **Decision support / priority queue** — `decision_support_service`.
- **Coordination intelligence** — `coordination_intelligence_service`.
- **Adoption / executive / organizational summaries** — analytics services.

See `truth-contracts.md` for why these must never be treated as sources of truth.
