# BetavanX — Architecture Glossary

**Status:** Implemented (documentation)

Canonical terminology for BetavanX architecture documents.
When docs disagree, this glossary is the reference.

---

## Activity Instance

**Status:** Future (runtime) — Implemented (schema foundation)

**Canonical operational data entity.**

An executable operational work unit created from:

```
WBS Template + Location + Workflow Context = Activity Instance
```

Examples:

- Concrete Column @ Tower A / Floor 2
- Block Work @ Zone East

Represents real construction work in the target Operational Graph.
Defined in `backend/core_operational/` as `ActivityInstance`.

**Do not confuse with:** Daily Work Order (current runtime entity).

---

## Operational Task

**Status:** Implemented (UX label)

**User-facing operational label** for work visible in dashboards,
work orders, and field reporting flows.

In current runtime, operational tasks map to **Daily Work Orders** (`task_id`).
In target architecture, operational tasks will often represent or surface
**Activity Instances**.

**Rule:**

| Term | Use for |
|------|---------|
| Activity Instance | Data model, schema, graph architecture |
| Operational Task | UI labels, operator language, reports |

These are related but not identical today.

---

## WBS Template

**Status:** Partial

Construction activity **type** — a reusable taxonomy entry, not a schedule row.

Examples: Concrete Column, Excavation, Slab Reinforcement.

WBS Templates define **what kind of work** exists in construction knowledge.
They do not define **when** work must happen.

Canonical catalog: `wbs-template-library.md`

---

## Workflow

**Status:** Future (runtime) — Implemented (architecture)

Possible operational execution paths between construction activities.

Workflows are **graph-based** and may branch.
They suggest paths; they do not force a single linear sequence.

Related entities: `WorkflowNode`, `WorkflowEdge`

---

## Workflow Context

**Status:** Open Question

The contextual input used with WBS Template and Location when creating
an Activity Instance.

Not yet formally modeled as a single schema field or entity.
See `open-architecture-questions.md`.

---

## Dependency

**Status:** Future (runtime) — Implemented (schema foundation)

Operational relationship between activity instances.

Supported types in foundation schema: FS, SS, FF, lag.

Dependencies express execution relationships — not WBS hierarchy.

---

## Constraint

**Status:** Open Question

Operational limitation or blocker affecting execution.

In current runtime, partial constraint behavior exists through
**Lifecycle Blockers** on work orders.

A dedicated graph-level Constraint entity is not yet defined.
See `open-architecture-questions.md`.

---

## Location Node

**Status:** Future (runtime) — Implemented (schema foundation)

A node in the construction location hierarchy.

Examples: Tower, Floor, Zone, Room, Sector.

Activities are instantiated **per location** in the target model.

---

## Operational Capability

**Status:** Partial

Platform intelligence behavior that monitors, analyzes, or reacts to
operational execution — **not** a construction deliverable.

Examples: delay monitoring, KPI analytics, recommendations, forecasting.

Canonical catalog: `operational-capability-model.md`

Operational capabilities must not be placed inside the WBS taxonomy.

---

## Schedule

**Status:** Prototype (visualization)

The **current operational arrangement** of executable work over time.

In BetavanX architecture:

- Schedule is **not** the system core
- Schedule is derived from activities, dependencies, and execution reality
- Schedule changes when the operational graph changes

---

## Gantt View

**Status:** Prototype

A **visualization layer** for schedule arrangement.

The Gantt chart shows operational graph state; it does not own execution logic.
Implemented today only as a lightweight planning prototype — not production CPM.

**Rule:** Gantt = visualization only.

---

## Operational Graph

**Status:** Target Architecture

The full target system of executable operational entities and relationships:

- Activity Instances
- Location structure
- Workflow paths
- Dependencies
- Resources and assignments
- Progress logs

This is the true operational system underneath schedule visualization.

---

## Operational Task Graph

**Status:** Target Architecture

Synonym for the executable operational graph viewed as connected
operational work nodes and paths.

Prefer **Operational Graph** in new documentation.
Use **Operational Task Graph** only when emphasizing node-to-node execution paths.

---

## Daily Work Order

**Status:** Implemented

Current runtime executable work unit.

Stored in `daily_work_orders`, keyed by `task_id`.
Linked to daily reports, KPI history, lifecycle, and validation.

This is the **production execution entity today**.
It is not yet replaced by Activity Instance.

---

## Daily Report

**Status:** Implemented

Current runtime field reporting entity.

Captures actual quantities, manpower, equipment, materials, delays, and status.
Feeds KPI, validation, lifecycle, and recommendations.

In target architecture, progress truth moves toward **ProgressLog** on
Activity Instances — but Daily Report remains the current production truth layer.

---

## Quick Reference

| Term | Layer | Status |
|------|-------|--------|
| Daily Work Order | Runtime MVP | Implemented |
| Daily Report | Runtime MVP | Implemented |
| Activity Instance | Target Graph | Future (schema: foundation) |
| WBS Template | Foundation / Target | Partial |
| Workflow Graph | Target | Future |
| Schedule View | Visualization | Prototype |
| Gantt View | Visualization | Prototype |
| Operational Capability | Platform layer | Partial |

See also: `current-vs-target-architecture.md`, `open-architecture-questions.md`
