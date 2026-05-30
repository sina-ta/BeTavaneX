# BetavanX — Current vs Target Architecture

**Status:** Implemented (documentation)

This document reconciles three coexisting architecture layers in BetavanX.
It describes **current implementation reality**, not a redesign.

---

## Why This Document Exists

BetavanX documentation previously mixed:

1. what the platform **runs today**
2. what exists as **schema foundation**
3. what the platform **targets** as operational graph architecture

Readers must not assume the Operational Graph is live production behavior
because graph entities and planning UX exist in documentation or prototype form.

---

## Layer 1 — Runtime MVP

**Status:** Implemented

This is the current production reality of BetavanX.

### Purpose

Operational construction visibility through daily execution reporting,
KPI monitoring, validation, lifecycle tracking, and recommendations —
centered on work orders and field reports.

### Core Runtime Components

| Component | Role | Status |
|-----------|------|--------|
| Projects | Project context via `project_id` on work orders | Partial |
| Daily Work Orders | Primary executable work unit in runtime (`task_id`) | Implemented |
| Daily Reports | Field operational truth input | Implemented |
| Dashboard | Operational overview and KPI strip | Implemented |
| KPI Engine | CPI, SPI, progress aggregation | Implemented |
| Validation Engine | Report trust and reliability pipeline | Implemented |
| Lifecycle Engine | Work-order execution state and blockers | Implemented |
| Recommendations | Operational decision suggestions | Implemented |

### Runtime Data Model (Current)

Primary tables in active use:

- `daily_work_orders`
- `daily_reports`
- `kpi_history`

Lifecycle and validation maintain their own active tables.
Workforce tables exist only when the workforce extension is enabled.

### Current API Structure

Entry point: `backend/api.py`

**Always mounted routers:**

| Router | Key endpoints |
|--------|----------------|
| Dashboard | `GET /dashboard` |
| Work Orders | `POST /daily-work-order`, `GET /daily-work-orders` |
| Reports | `POST /daily-report`, `GET /daily-reports` |
| Task Detail | `GET /task/{task_id}` |
| Analytics | `GET /analytics/kpi-trends`, `GET /analytics/kpi-trends/{task_id}` |
| Validation | `/validation/*` |
| Lifecycle | `/lifecycle/*` |

**Optional extension (env-gated):**

| Extension | Flag | Router |
|-----------|------|--------|
| Workforce | `BETAVANX_ENABLE_WORKFORCE_EXTENSION` | `/workforce/*` |

Recommendations are produced through dashboard and task-detail services;
they are not a separate public router in the current runtime.

### Runtime Identity

In the current MVP, **task** means a daily work order row keyed by `task_id`.
It is not yet the same entity as `ActivityInstance` in the operational graph schema.

---

## Layer 2 — Core Operational Foundation

**Status:** Implemented as foundation — not yet wired into runtime

### Purpose

Foundational schema for the target Operational Graph.
Defines construction-native entities and relationships without implementing
a scheduling engine, graph mutation engine, or full planning backend.

### Location

```
backend/core_operational/
├── models/
├── schemas/
├── enums/
├── relationships/
└── docs/
```

### Entities

| Entity | Purpose |
|--------|---------|
| Project | Operational project container |
| WbsTemplate | Construction activity taxonomy (not schedule rows) |
| LocationNode | Hierarchical execution location |
| WorkflowNode | Possible operational workflow node types |
| WorkflowEdge | Graph-based possible execution paths |
| ActivityInstance | Executable operational entity |
| Dependency | Activity-to-activity relationships |
| Resource | Lightweight manpower / material / equipment |
| Assignment | Resource allocation to activity instance |
| ProgressLog | Operational progress truth on activity instances |

### Current Foundation State

- SQLAlchemy models and Pydantic schemas exist
- Conceptual relationship map exists
- Models are **not imported** in `backend/api.py`
- Tables are **not created** by current runtime startup
- No public API exposes these entities yet

This layer is **schema foundation**, not production behavior.

---

## Layer 3 — Target Operational Graph Architecture

**Status:** Target Architecture

### Purpose

BetavanX target execution model:

```
WBS Template
+
Location
+
Workflow Context
================
Activity Instance
```

### Target Characteristics

- Graph-based workflow (branching, optional paths)
- Location-aware activity instantiation
- Dependencies between activity instances
- Progress logs as operational truth on activities
- Schedule View / Gantt as visualization only — not the system core

### Target Supporting Concepts

| Concept | Target role |
|---------|-------------|
| Workflow Graph | Possible execution paths |
| Location Graph | Where work happens |
| Operational Graph | Executable activities + dependencies + progress |
| Schedule View | Temporary visualization of graph state |
| Operational Capabilities | Intelligence layers above execution entities |

### Current Target Artifacts (Non-Production)

| Artifact | Status |
|----------|--------|
| Architecture docs (`core-operational-model.md`, `workflow-graph.md`, etc.) | Implemented |
| `backend/core_operational/` schema | Implemented (foundation) |
| `/dashboard/planning` frontend prototype | Prototype (localStorage, no backend API) |

The planning prototype validates UX and operational language.
It does not represent the production graph engine.

---

## Component Status Matrix

| Component | Status |
|-----------|--------|
| Daily Work Orders | Implemented |
| Daily Reports | Implemented |
| Dashboard | Implemented |
| KPI Engine | Implemented |
| Validation Engine | Implemented |
| Lifecycle Engine | Implemented |
| Recommendations | Implemented |
| Projects (runtime) | Partial |
| Workforce Extension | Partial (optional, env-gated) |
| `backend/core_operational/` schema | Implemented (foundation, unwired) |
| Activity Instance (runtime) | Future |
| Workflow Graph (runtime) | Future |
| Location Graph (runtime) | Future |
| Dependency engine | Future |
| Schedule View / Gantt (platform) | Prototype |
| Planning prototype UI | Prototype |
| Operational Graph (full) | Future |
| Constraint entity (graph-level) | Future |
| Bridge: Work Order ↔ Activity Instance | Future |

---

## Documentation Boundaries

| Topic | Canonical document |
|-------|-------------------|
| Terminology | `glossary.md` |
| Platform layers diagram | `core-platform-diagram.md` |
| WBS construction taxonomy | `wbs-template-library.md` |
| Platform capabilities | `operational-capability-model.md` |
| Open unresolved questions | `open-architecture-questions.md` |
| Target entity model | `core-operational-model.md` |

---

## Summary

BetavanX today is an **Operational Construction Visibility Platform** running
on Daily Work Orders and Daily Reports, with validation, lifecycle, KPI, and
recommendations as active core engines.

The **Operational Graph** is the documented target architecture and schema
foundation — not yet the live execution backbone.

Documentation must keep these layers separate until an explicit integration
bridge is implemented.
