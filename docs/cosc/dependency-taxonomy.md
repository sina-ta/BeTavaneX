# COSC — Dependency Semantics Taxonomy

> Formalization of the dependency types **already implied** by the BetavanX
> runtime. This is semantic extraction, not scheduling, optimization, or a graph
> engine. Every category below is justified by real code (models, services,
> analytics); speculative dependency types are deliberately excluded.
>
> The single most useful distinction in this document is **enforcement status**:
>
> - **Enforced** — the runtime actively guards or propagates the dependency.
> - **Declared** — the dependency is modeled (a column/field/FK exists and reads
>   like a dependency) but **nothing in the runtime enforces it**.
> - **Observed** — the dependency exists only as an interpretation in the
>   analytics layer; it changes signals, never state.
>
> Calling a declared-only relationship a "dependency" without this label is how
> the system currently misleads its readers (see `semantic-fragility-audit.md`).

---

## 1. Dependency matrix

| Dependency | Source → Target | Carrier (where it lives) | Enforcement | Blocking? | Propagation |
|---|---|---|---|---|---|
| `containment_dependency` | child → parent | FK `RESTRICT` / `SET NULL` / `CASCADE` | **Enforced** | Yes (delete-time) | Delete-restrict upward |
| `spatial_dependency` | ActivityInstance → Location | `location_id` FK + `(project,wbs,location)` unique | **Enforced** (existence/uniqueness) | Yes (create-time) | None at runtime |
| `execution_dependency` | WorkflowStep ← WorkOrder weight | `WorkOrderWorkflowStep.execution_weight` + `ProgressService` | **Enforced** | No | Pull, bottom-up, unweighted |
| `coordination_dependency` | WorkOrder ↔ WorkflowStep; role ↔ role | assignment junction + coordination analytics | **Enforced** (link) / **Observed** (handoff) | No | None (link) / signal (handoff) |
| `governance_dependency` | WorkflowStep → Approval/Inspection | `WorkflowGovernanceService` | **Enforced** (partial) | Partial (one guard) | Step status only |
| `readiness_dependency` | WorkflowStep → "ready to run" | `WorkflowStep.ready` (bool) | **Declared** (unowned) | No | None |
| `resource_dependency` | WorkflowStep → resources/permits/docs/BOQ | template JSONB, daily-report counts, `BOQMapping` | **Declared** (descriptive) | No | None |
| `informational_dependency` | analytics ← evidence/audit | DailyReport, audit/usage JSONL | **Observed** | No | Signal only |

> Read this matrix as the contract: only `containment`, `spatial`, `execution`,
> the link half of `coordination`, and the guarded half of `governance` are real
> runtime dependencies. The rest are meaning that the data *implies* but the
> runtime does *not* uphold.

---

## 2. Dependency semantics

Each category is defined by: operational meaning · propagation meaning · blocking
semantics · authority · temporal implications · execution consequences · lifecycle
interaction.

### 2.1 `containment_dependency` (structural substrate) — Enforced

- **Operational meaning.** Operational data only exists *inside* a parent: WBS,
  Locations, BOQ, and Activities require a `Project`; WorkflowSteps require an
  `ActivityInstance`; DailyReports require a `WorkOrder`; etc. This is the
  planning-hierarchy spine.
- **Propagation meaning.** Propagates **at delete time** only. `RESTRICT` means a
  parent cannot be removed while children exist; `SET NULL` (WBS/Location
  `parent_id`) re-roots children; `CASCADE` (`WorkOrderWorkflowStep.work_order_id`,
  `project_memberships.project_id`) removes dependents with the parent.
- **Blocking semantics.** Blocks **deletion**, not execution. You cannot erase a
  project/step/work order that has history beneath it.
- **Authority.** PostgreSQL FK constraints + `integrity/delete_policy`
  (only `WorkOrderWorkflowStep` and `BOQMapping` are deletable at all).
- **Temporal implications.** Parent must exist *before* child creation; order of
  creation is strictly top-down.
- **Execution consequences.** History is immutable by construction; corrections
  happen by adding/removing the two allowed junctions, never by deleting cores.
- **Lifecycle interaction.** Lifecycles end in a terminal *status*, not row
  removal — containment is why "delete" is not part of any lifecycle.

### 2.2 `spatial_dependency` — Enforced (existence/uniqueness), no sequencing

- **Operational meaning.** Real work is located: an `ActivityInstance` is the
  unique intersection of a `WBSItem` (*what*) and a `Location` (*where*), enforced
  by `(project_id, wbs_item_id, location_id)` uniqueness.
- **Propagation meaning.** None at runtime. The Location tree (`parent_id`)
  classifies space but no logic propagates state across zones/floors.
- **Blocking semantics.** Blocks **creation** of an activity without a valid
  location; blocks a duplicate activity at the same WBS×Location. Does **not**
  block execution based on neighboring locations.
- **Authority.** FK + unique constraints on `activity_instances` / `locations`.
- **Temporal implications.** Location must exist before the activity; no temporal
  ordering between locations.
- **Execution consequences.** Locks the "one activity per scope-place" rule; there
  is no spatial sequencing (e.g. "floor 1 before floor 2") in the runtime.
- **Lifecycle interaction.** `Location` has its own `ACTIVE → CLOSED` lifecycle but
  closing a location does **not** cascade to its activities (declared, not
  enforced beyond the FK).

### 2.3 `execution_dependency` — Enforced (the core real dependency)

- **Operational meaning.** A `WorkflowStep`'s realized progress depends on the
  **completion of WorkOrders** committed to it. The commitment is
  `WorkOrderWorkflowStep.execution_weight`; the trigger value is
  `WorkOrder.status == "COMPLETED"`.
- **Propagation meaning.** Bottom-up, **pull-based**:
  `step = Σ(weight where WO COMPLETED) / Σ(all weight) × 100` →
  `activity = mean(step progress)` → `project = mean(activity progress)`
  (`ProgressService`). Activity/project roll-ups are **unweighted** (`planned_weight`
  is ignored).
- **Blocking semantics.** None. Progress is a measurement, not a gate; nothing is
  blocked by low progress.
- **Authority.** `ProgressService` is the sole owner of the formula. No other layer
  may compute progress.
- **Temporal implications.** Progress only moves when a WorkOrder reaches
  `COMPLETED`. There is **no automatic recompute**: the cached
  `workflow_steps.progress_percent` is written only by an unsurfaced method, so the
  live value exists only when something recomputes on read (see fragility F2/F3).
- **Execution consequences.** A step with no linked work orders is permanently 0%
  (empty denominator). Completing a work order changes derived progress but pushes
  nothing — consumers must recompute.
- **Lifecycle interaction.** Progress is **independent** of step `status`. A step
  can be `APPROVED` at 0% progress, or 100% progress while `PLANNED`. Progress and
  status are two unsynchronized truths of "done."

### 2.4 `coordination_dependency` — Enforced (link) + Observed (handoff)

- **Operational meaning.** Two faces:
  (a) **Structural link** — a `WorkOrder` is bound to a `WorkflowStep` via the
  assignment junction (the unit of field coordination).
  (b) **Role handoff** — worker→supervisor (report→approval) and
  supervisor→worker (assignment→reporting) dependencies, surfaced by
  `coordination_intelligence_service` as `cross_role_dependencies`
  (`from_role`/`to_role`).
- **Propagation meaning.** The link itself does not propagate state. The handoff
  side propagates only into **coordination signals** (bands ALIGNED / FRAGMENTED /
  STRESSED), never into domain state.
- **Blocking semantics.** Link creation blocks **duplicates**
  (`(work_order, workflow_step)` unique + duplicate-assignment guard/alert). Handoff
  gaps block nothing — they are advisory.
- **Authority.** `WorkflowExecutionService.assign_work_order_to_workflow_step` owns
  the link; analytics own the handoff interpretation.
- **Temporal implications.** Both WorkOrder and WorkflowStep must exist before the
  link. Handoff signals are time-windowed (`OPS_*` thresholds, 7-day windows).
- **Execution consequences.** The link is what makes a work order's weight count
  toward a step (so coordination feeds execution). Handoff signals inform humans;
  they trigger no automatic assignment/approval.
- **Lifecycle interaction.** The link is one of two **deletable** carriers
  (correctable). Handoffs reference live statuses (`ASSIGNED`/`IN_PROGRESS`,
  pending approvals) but do not change them.

### 2.5 `governance_dependency` — Enforced (partial)

- **Operational meaning.** A `WorkflowStep`'s authoritative acceptance depends on a
  governance act: approval, and (loosely) inspection outcome.
- **Propagation meaning.** Approval propagates to **step status** only
  (`approve_workflow_step` and `mark_inspection_passed` set `status = APPROVED`).
  It does **not** propagate to activity/project status.
- **Blocking semantics.** Two real guards: `mark_inspection_passed` requires
  `status == INSPECTION_PENDING`; `approve_workflow_step` blocks a duplicate
  `APPROVED` of the same `approval_type`. **Everything else is unguarded** — a step
  can be approved from any state, and inspection is not a hard precondition of
  approval (fragility F5).
- **Authority.** `WorkflowGovernanceService` exclusively. (Attribution, however, is
  client-supplied via `approved_by` — fragility F1.)
- **Temporal implications.** Approval/inspection occur after execution by
  convention, not by enforcement.
- **Execution consequences.** `APPROVED` is the strongest acceptance state yet the
  least protected; it can be reached without inspection, with an open critical
  blocker, or directly at creation.
- **Lifecycle interaction.** Governance owns the step status transitions but shares
  the `APPROVED` target with `mark_inspection_passed`, giving the state two
  meanings depending on its origin.

### 2.6 `readiness_dependency` — Declared (unowned)

- **Operational meaning.** A `WorkflowStep` carries `ready: bool` that reads as
  "this step is ready to be executed." Assignment also implies an *existence
  readiness* (both work order and step must exist to be linked).
- **Propagation meaning.** None. **No service computes or flips `ready`.** It is
  whatever was passed at creation and never changes.
- **Blocking semantics.** None. `ready` is a filterable flag, but no operation is
  gated on it. (Existence readiness for assignment *is* enforced: a missing work
  order or step raises before a link is created.)
- **Authority.** Ambiguous — there is no owner. `WorkflowStepCreate` accepts it from
  the client; nothing derives it (fragility F8).
- **Temporal implications.** Implies "prerequisites satisfied" but encodes no
  prerequisite relationships and no time semantics.
- **Execution consequences.** Filtering on `ready=true` reflects a stale
  creation-time guess, not actual readiness.
- **Lifecycle interaction.** Disconnected from status and progress; it is the
  clearest example of a declared dependency masquerading as enforced.

### 2.7 `resource_dependency` — Declared (descriptive only)

- **Operational meaning.** Steps depend on resources/permits/documents to be
  executable, and on BOQ allocation to be costable:
  `WorkflowStepTemplate.required_resources / required_permits / required_documents`
  (JSONB), `DailyReport.reported_manpower / reported_equipment /
  reported_material_entries`, and `BOQMapping` (quantity/cost allocation).
- **Propagation meaning.** None. No runtime checks resource availability, permit
  presence, or document completeness; reported counts are descriptive numbers.
- **Blocking semantics.** None. A step executes and gets approved regardless of
  whether required permits/resources are recorded. `BOQMapping` only constrains its
  own arithmetic (`allocated_quantity > 0`, etc.), not execution.
- **Authority.** Template knowledge is reference data; `BOQMapping` is owned by
  `WorkflowExecutionService.link_boq_item`. Neither enforces a resource gate.
- **Temporal implications.** None encoded.
- **Execution consequences.** Resource requirements are guidance for humans, not
  preconditions. BOQ allocation is planned cost/quantity, never actual spend or
  earned value.
- **Lifecycle interaction.** `BOQMapping` is the second **deletable** carrier;
  template archival does not invalidate steps that referenced it.

### 2.8 `informational_dependency` — Observed (analytics)

- **Operational meaning.** Operational interpretation depends on evidence and
  activity logs: daily reports, the audit ledger, usage events, and now the
  operational event ledger.
- **Propagation meaning.** Propagates into **signals**, not state:
  reporting cadence, conflict spikes, workload imbalance, health bands, decision
  queues, coordination bands (`operational_/decision_/coordination_intelligence`).
- **Blocking semantics.** None. Missing information lowers a health score or raises
  a "reporting gap" signal; it never blocks an operation.
- **Authority.** Analytics services (read-only leaves). They write no domain state.
- **Temporal implications.** Heavily time-windowed (`OPS_STALL_DAYS`,
  `OPS_APPROVAL_DELAY_DAYS`, 7-day windows). Stale `updated_at` is itself an
  informational dependency (stagnation).
- **Execution consequences.** Advisory only; severity `info/warning/critical`
  triggers no automatic action.
- **Lifecycle interaction.** Reads statuses/timestamps across many entities but
  changes none. Some inferred concepts (e.g. `PENDING` approvals) are not even
  produced by the runtime (fragility F10) — an informational dependency on a state
  that does not occur.

---

## 3. Propagation rules

What actually propagates, and how. (Everything not listed here does **not**
propagate.)

1. **Execution → progress (pull, bottom-up).**
   `WorkOrder.status=COMPLETED` ⇒ step progress ⇒ activity mean ⇒ project mean.
   Computed on demand; unweighted at roll-up; cached value not auto-refreshed.
2. **Governance → step status (direct, local).**
   `approve` / `inspection passed` ⇒ `WorkflowStep.status = APPROVED`. Stops at the
   step — no activity/project status propagation exists.
3. **Containment → deletion (upward block / downward cascade).**
   `RESTRICT` blocks parent deletion; `CASCADE` removes junction/membership
   dependents; `SET NULL` re-roots WBS/Location children.
4. **Coordination link → execution eligibility.**
   Creating `WorkOrderWorkflowStep` is what allows a work order's weight to enter
   the step's progress formula. Removing it withdraws that contribution.
5. **Information → signals (observational).**
   Evidence/audit/usage ⇒ analytics bands and queues. One-way; never returns to
   state.

**Non-propagation (by design or by gap):**
- Blockers do **not** propagate to status or progress (inert; fragility F9).
- `ready` does **not** propagate anywhere.
- Resource/permit/document requirements do **not** gate anything.
- Status changes do **not** cascade up the planning hierarchy (a completed step
  does not complete its activity/project).

---

## 4. Invalid dependency patterns

Patterns that violate the intended semantics and are **currently possible** (the
runtime does not prevent them). Listed so they can be guarded later without a
redesign.

1. **Cross-project execution link.** `assign_work_order_to_workflow_step` checks
   only that both rows exist, not that they belong to the **same project**. A work
   order from project A can be linked to a step in project B. Consequence: progress
   silently ignores it (the formula lists work orders by the step's project), so the
   weight becomes a dangling, invisible commitment.
2. **Cross-project BOQ allocation.** `link_boq_item` does not check that the
   `BOQItem` and `WorkflowStep` share a project. A step can consume another
   project's budget line.
3. **Cyclic containment.** WBS and Location `parent_id` are self-referential with
   no cycle check; a node can be made its own ancestor, producing an infinite tree.
4. **Governance without precedence.** A step can be `APPROVED` with no inspection,
   with an open `CRITICAL` blocker, or at creation time — the governance dependency
   is bypassable.
5. **Fabricated execution state at creation.** `WorkflowStepCreate` accepts
   arbitrary `status` / `progress_percent` / `ready`, so a step can be "born done"
   with no underlying execution dependency satisfied.
6. **Phantom readiness.** `ready=true` with none of its implied prerequisites met,
   because nothing computes the flag.
7. **Orphaned commitment.** An `execution_weight` whose work order never reaches
   `COMPLETED` (or is later moved back) silently changes the denominator without any
   reconciliation event.
8. **Dependency on a non-existent state.** Analytics depend on `PENDING`/
   `UNDER_REVIEW` approvals that the write path never creates — an informational
   dependency on an unreachable state.

> None of these are fixed here (audit/formalization only). Each maps to a
> finding in `semantic-fragility-audit.md`.

---

## 5. Dependency authority summary

| Dependency | Single owner today? | Owner |
|---|---|---|
| containment | Yes | DB FKs + `delete_policy` |
| spatial | Yes | DB constraints |
| execution | Yes | `ProgressService` |
| coordination (link) | Yes | `WorkflowExecutionService` |
| coordination (handoff) | Yes (read) | coordination analytics |
| governance | Yes (but bypassable) | `WorkflowGovernanceService` |
| readiness | **No owner** | — (declared on the model, set by client) |
| resource | Split / none enforce | template data + `WorkflowExecutionService` (BOQ) |
| informational | Yes (read) | analytics services |

The two governance/coordination authorities are real; the **missing owner for
readiness** and the **non-enforcing owners for resource** are the taxonomy's
weakest points.

---

## 6. Future graph-readiness implications

The runtime already forms an **implicit operational DAG** — this taxonomy is the
edge vocabulary for it. Recording this does **not** mean building a graph database,
scheduler, or optimizer (explicitly out of scope). It means: if a graph view is
ever derived later, these are the edges and the rules it must respect.

Implicit nodes and edges already present:

```
Project ──contains──▶ WBSItem / Location / BOQItem / ActivityInstance
ActivityInstance ──contains──▶ WorkflowStep
WorkflowStep ──governed_by──▶ Approval / Inspection
WorkflowStep ──constrained_by──▶ Blocker            (observed only)
WorkflowStep ──allocates──▶ BOQItem (via BOQMapping)
WorkflowStep ◀──commits── WorkOrder (via WorkOrderWorkflowStep, weighted)
WorkOrder ──evidenced_by──▶ DailyReport
```

What "graph-ready" would require (semantic preconditions, not implementation):

1. **Edge integrity.** Same-project invariants on `WorkOrderWorkflowStep` and
   `BOQMapping` (close invalid patterns #1/#2) so edges can't cross aggregates.
2. **Acyclicity.** Cycle guards on WBS/Location parent edges (#3) so the hierarchy
   is a true tree/DAG.
3. **Owned readiness.** A single deriver for `ready` so a "readiness edge" means
   something (#6) — today it would be a meaningless edge.
4. **Explicit edge types.** This document's eight categories are the candidate
   edge labels; each already has defined propagation/blocking semantics above.
5. **Causality threading.** The new event ledger's `causality_reference`
   (`event-ledger-foundation.md`) is the natural place to record *temporal* edges
   between operations without touching state — a lineage graph, separate from the
   structural graph.
6. **Status vs progress reconciliation.** A graph that asks "is this node done"
   needs one answer; today `COMPLETED` / `APPROVED` / `progress=100` disagree
   (fragility F16).

Until those preconditions hold, any graph view would faithfully reproduce the
current ambiguities. The value of this taxonomy is to make the edges — and their
real enforcement status — explicit **before** anyone builds on top of them.

---

## 7. Summary

- The runtime has **three genuinely enforced** dependency types
  (`containment`, `spatial`, `execution`), **one half-enforced** (`governance`),
  **one mixed** (`coordination`: link enforced, handoff observed), **two
  declared-but-unenforced** (`readiness`, `resource`), and **one observational**
  (`informational`).
- Only execution and governance propagate to state, and only locally (progress
  bottom-up; status to the step). Nothing cascades up the planning hierarchy.
- The word "dependency" is currently overloaded: several modeled relationships
  imply constraints the runtime never applies. This taxonomy's contribution is to
  label each one's true enforcement status so future work builds on what is real.
