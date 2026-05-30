# Runtime to Operational Graph Bridge Design

**Status:** Implemented (architecture design — documentation only)

**Purpose:** Design the transition path between the **Current Runtime MVP** and the
**Future Operational Graph Architecture**.

**Constraint:** This document does not authorize code changes, schema changes, API
creation, or graph runtime implementation.

**Related documents:**

- `current-vs-target-architecture.md`
- `glossary.md`
- `audits/core-operational-foundation-audit.md`
- `open-architecture-questions.md`
- `core-operational-model.md`

---

## SECTION 1 — Current Runtime Reality

**Status:** Implemented (production behavior today)

### Operational Flow

```
Project (lightweight project_id)
        ↓
Daily Work Orders (task_id — primary executable unit)
        ↓
Daily Reports (field submission)
        ↓
Validation Engine (report trust & anomaly pipeline)
        ↓
Lifecycle Engine (work-order / task execution state & blockers)
        ↓
Dashboard (+ KPI Engine, Recommendations, Analytics)
```

### What Each Layer Does Today

| Layer | Role | Primary entities |
|-------|------|------------------|
| **Project** | Lightweight grouping via `project_id` on work orders | Integer reference — no full `core_operational.Project` row |
| **Daily Work Orders** | Executable work unit operators interact with | `daily_work_orders` keyed by `task_id` |
| **Daily Reports** | Field capture of actual execution | `daily_reports` linked to `work_order_id` |
| **Validation** | Trust scoring, anomaly detection, reporter reliability | Validation pipeline on report + work order context |
| **Lifecycle** | Execution state transitions, operational blockers | `TaskLifecycle`, `WorkOrderLifecycle`, `OperationalBlocker` |
| **Dashboard** | Operational visibility, KPI strip, recommendations | Aggregated from work orders, reports, KPI history |

### What Currently Acts as Operational Truth

BetavanX runtime truth today is **report-driven and work-order-centric**:

1. **Daily Report** — primary field truth input
   - Actual quantity, manpower, equipment, materials, delay reason, weather, status
   - Submitted by `reported_by` (lightweight string — not mandatory workforce entity)

2. **Daily Work Order** — operational anchor
   - Planned quantity, assignment label (`assigned_to`), priority, status
   - All validation, lifecycle, KPI, and task-detail flows key off `task_id` / work order

3. **KPI History** — derived analytical truth
   - CPI, SPI, progress percent computed from reports and work order context
   - Used by dashboard and performance views

4. **Validation results** — trust overlay on reports
   - Does not replace the report; annotates reliability

5. **Lifecycle state** — execution state overlay on work orders
   - Blockers affect operational readiness; not graph-native constraints

**Summary:** Operational truth = **Daily Reports on Daily Work Orders**, enriched by
validation and lifecycle, summarized by KPI and dashboard layers.

There is no Activity Instance, ProgressLog, WBS graph, or location graph in runtime today.

---

## SECTION 2 — Target Operational Graph

**Status:** Target Architecture (schema foundation exists — not wired)

### Operational Flow

```
Project
        ↓
WBS Template (construction taxonomy)
        +
Location Node (execution geography)
        +
Workflow Context (path / node context)
        ↓
Activity Instance (canonical executable entity)
        ↓
Progress Log (operational truth on activities)
        ↓
Operational Graph (activities + dependencies + workflow + resources)
        ↓
Operational Capabilities (validation, lifecycle, analytics — graph-aware)
        ↓
Schedule View / Gantt View (visualization only)
```

### What Each Layer Means in Target Architecture

| Layer | Role |
|-------|------|
| **Project** | Full operational container owning templates, locations, workflow, activities |
| **WBS Template** | Construction activity **type** — what kind of work (not when) |
| **Location Node** | Where work happens — tower, floor, zone, etc. |
| **Workflow** | Possible execution paths (WorkflowNode + WorkflowEdge) |
| **Activity Instance** | Executable operational entity — canonical data model |
| **Progress Log** | Append-only operational truth on activity execution |
| **Operational Graph** | Connected activities, dependencies, assignments, resources |
| **Schedule View** | Temporary time visualization — not the system core |

### Future Operational Truth Model

In the target architecture, truth moves **activity-centric**:

1. **ProgressLog** — primary operational truth layer on `ActivityInstance`
   - Progress percent, quantities, manpower, materials, equipment, delays, issues
   - Append-only execution history

2. **ActivityInstance** — canonical executable entity
   - Holds current snapshot state (`operational_status`, `progress_percent`)
   - Linked to WBS Template, Location, optional Workflow Context

3. **Dependency + Workflow Graph** — coordination truth
   - Describes what *can* happen and what *must* happen between activities
   - Not schedule truth — arrangement truth

4. **Operational Capabilities** — intelligence overlay
   - Validation, lifecycle, analytics operate on graph entities
   - Capabilities are not embedded in WBS

**Summary:** Operational truth = **Progress Logs on Activity Instances** within an
Operational Graph — visualized through Schedule View, not driven by static WBS sequence.

---

## SECTION 3 — Concept Mapping

**Status:** Partial (bridge design — mappings are proposals, not implemented)

| Current Runtime Concept | Future Graph Concept | Mapping Type | Notes |
|-------------------------|---------------------|--------------|-------|
| Project (`project_id` int) | `core_operational.Project` | **Partial** | Runtime uses lightweight ID; graph uses full project entity. Requires project registry bridge. |
| Daily Work Order | Activity Instance | **Partial** | Same operational role (executable work), different model richness. Not 1:1 without WBS + Location. |
| `task_id` | Activity Instance ID | **Partial** | Different ID spaces today. Bridge needs explicit FK or mapping table. |
| Daily Report | ProgressLog | **Partial** | Similar field data; report is work-order-bound, log is activity-bound. |
| Work order `status` | Activity `operational_status` | **Partial** | Overlapping vocabulary; lifecycle states are richer than activity status enum. |
| Work order `assigned_to` (string) | Assignment → Resource | **Partial** | Runtime uses free-text; graph uses Resource + Assignment. Workforce extension adds another layer. |
| Work order `planned_qty` / `unit` | Assignment `planned_quantity` + WBS hints | **Partial** | Planned work splits across activity and resource assignment in graph model. |
| Report `actual_qty` | ProgressLog `completed_quantity` | **Direct** (semantic) | Strong field-level correspondence. |
| Report `manpower_count` | ProgressLog `manpower_used` | **Direct** (semantic) | Strong correspondence. |
| Report `material_consumption` | ProgressLog `material_usage` | **Direct** (semantic) | Strong correspondence. |
| Report `equipment_hours` | ProgressLog `equipment_hours` | **Direct** (semantic) | Strong correspondence. |
| Report `delay_reason` | ProgressLog `operational_notes` / `issues` | **Partial** | Delay maps to notes/issues; no dedicated delay field on ProgressLog schema today. |
| Report `reported_by` | ProgressLog `reported_by` | **Direct** (semantic) | Same lightweight reporter pattern. |
| KPI History (`task_id`) | Derived from Activity Instance progress | **Partial** | KPI today keys off work order; future keys off graph activity. |
| TaskLifecycle / WorkOrderLifecycle | Activity state + transitions | **Partial** | Lifecycle is richer and work-order-centric; graph lacks transition table. |
| OperationalBlocker | Constraint (graph) | **Partial** | Blockers exist today; Constraint entity does not exist in graph schema. |
| Validation pipeline (report) | Graph validation (activity/report) | **Partial** | Same engine philosophy; different anchor entity. |
| Recommendations (task context) | Recommendations (graph context) | **Partial** | Engine exists; input context must shift from task to activity/graph. |
| Dashboard task list | Activity / location graph views | **Partial** | UX aggregation changes; visibility goal stays the same. |
| Operational Task (UX label) | Operational Task (UX label) | **Direct** | Remains user-facing language regardless of backend entity. |
| Planning prototype activity | Activity Instance | **Partial** | Prototype mirrors concept; uses localStorage, string IDs, no backend. |
| WBS (none in runtime) | WbsTemplate | **No Mapping** | New capability — not present in runtime MVP. |
| Location (none in runtime) | LocationNode | **No Mapping** | New capability — not present in runtime MVP. |
| Workflow (none in runtime) | WorkflowNode / WorkflowEdge | **No Mapping** | New capability — not present in runtime MVP. |
| Dependency (none in runtime) | Dependency | **No Mapping** | New capability — not present in runtime MVP. |
| Schedule / Gantt (none in runtime) | Schedule View | **No Mapping** | Prototype only; not production runtime. |
| Workforce Worker (extension) | Resource (manpower) + Assignment | **Partial** | Optional extension; must not become mandatory for core bridge. |

### Mapping Summary

| Mapping Type | Count (approx.) | Meaning |
|--------------|-----------------|---------|
| **Direct** | 5 | Strong semantic 1:1 at field or label level |
| **Partial** | 18 | Related concept; requires adapter or enrichment |
| **No Mapping** | 5 | Graph-only concepts with no runtime equivalent today |

---

## SECTION 4 — Migration Strategies

**Status:** Open (strategies documented — no selection enforced here)

Three transition strategies are evaluated. **No strategy is chosen in this section.**

---

### Strategy A — Work Orders Remain Permanent; Activity Instance Added Later

**Description:**

Daily Work Orders continue as the primary runtime entity indefinitely.
Activity Instances are introduced as a parallel graph layer with optional
cross-reference (`activity_instance_id` on work order, or mapping table).

```
Runtime MVP (permanent)          Operational Graph (additive)
─────────────────────           ────────────────────────────
Daily Work Order        ←──?──→ Activity Instance
Daily Report            ←──?──→ ProgressLog
Lifecycle (work order)  ←──?──→ Activity state (optional)
```

**Pros:**

- Zero disruption to current MVP workflows
- Field teams keep familiar work order / report UX
- Validation, lifecycle, KPI engines continue unchanged initially
- Lowest risk for small construction teams adopting BetavanX
- Aligns with "visibility platform first" philosophy

**Cons:**

- Permanent dual-entity maintenance unless later merged
- Graph intelligence split across two anchors
- Risk of truth divergence (report vs progress log)
- Planning graph and runtime field reporting may feel disconnected
- Mapping table adds long-term complexity

**Best when:**

- Adoption speed and stability matter more than graph purity
- Projects operate primarily through daily reporting, not full planning

---

### Strategy B — Work Orders Become Activity Instances

**Description:**

Daily Work Orders are replaced by Activity Instances. Reports become ProgressLogs.
Migration converts existing rows; APIs shift to graph entities.

```
Daily Work Order  ──REPLACE──►  Activity Instance
Daily Report      ──REPLACE──►  ProgressLog
task_id           ──REPLACE──►  activity_instance.id
```

**Pros:**

- Single canonical entity — no dual truth
- Clean architecture alignment with glossary immediately
- Graph capabilities activate on one model
- Simplest long-term mental model for developers

**Cons:**

- Requires WBS + Location for every activity (MVP lacks these today)
- Breaks all existing APIs, dashboards, validation, lifecycle bindings
- Forces graph complexity on teams that only need daily reporting
- High migration risk for existing data (`task_id` references everywhere)
- Contradicts MVP philosophy of lightweight field adoption

**Best when:**

- Platform pivots fully to planning-first graph product
- Existing MVP user base is small or disposable

---

### Strategy C — Work Orders Become UX Layer; Activity Instance Becomes Truth Layer

**Description:**

Activity Instance becomes the **operational truth anchor** in the backend.
Daily Work Orders survive as a **field-friendly UX/reporting surface** — a simplified
projection or adapter over one activity (or a subset of activities).

```
┌─────────────────────────────────────┐
│   UX Layer (field-facing)           │
│   Daily Work Order · Daily Report   │
└──────────────┬──────────────────────┘
               │ adapter / projection
               ▼
┌─────────────────────────────────────┐
│   Truth Layer (graph)               │
│   Activity Instance · ProgressLog   │
│   Operational Graph                 │
└─────────────────────────────────────┘
```

**Pros:**

- Preserves simple field UX ("work order", "daily report")
- Graph becomes authoritative backend without forcing graph UX on field users
- Aligns with glossary: Operational Task = UX, Activity Instance = data
- Allows gradual migration: adapter first, full graph later
- Validation/lifecycle can evolve to graph-aware while UX stays familiar

**Cons:**

- Adapter layer adds engineering complexity
- Must define strict sync rules (report → progress log)
- Risk of adapter becoming a second hidden model if poorly bounded
- Requires clear ownership rules for state and progress

**Best when:**

- BetavanX remains a visibility platform with optional planning depth
- Field reporting and graph planning must coexist long-term

---

### Strategy Comparison

| Criterion | Strategy A | Strategy B | Strategy C |
|-----------|------------|------------|------------|
| MVP disruption | Low | High | Low–Medium |
| Architectural purity | Low | High | High |
| Field UX simplicity | High | Medium | High |
| Dual-entity risk | High (permanent) | None | Low (bounded adapter) |
| Graph readiness | Slow | Immediate | Phased |
| Implementation complexity | Low initially | High | Medium |
| Aligns with lightweight adoption | Strong | Weak | Strong |

---

## SECTION 5 — Recommended Direction

**Status:** Architecture recommendation (documentation only — not implementation approval)

Based on:

- current codebase (work-order-centric runtime; `core_operational` unwired)
- current architecture (three-layer model in `current-vs-target-architecture.md`)
- MVP philosophy (lightweight, field-oriented visibility platform)
- simplicity (no big-bang migration; optional graph depth)

### Recommendation: **Strategy C — phased through Strategy A**

BetavanX should evolve toward **Strategy C** as the **target bridge architecture**,
adopted in **phases** that begin with **Strategy A coexistence patterns**.

### Why Strategy C (not B)

Strategy B requires every field operation to understand WBS, Location, and Workflow —
contradicting BetavanX's MVP identity as a **daily reporting and visibility platform**
for construction teams that may never adopt full graph planning.

Replacing work orders would break validation, lifecycle, KPI, dashboard, and task-detail
flows that are implemented and working today.

### Why Strategy C (not permanent A)

Permanent Strategy A creates two equal truths (work order vs activity) with no
authority hierarchy. That contradicts the architecture docs and glossary, which
 designate **Activity Instance + ProgressLog** as the canonical operational model.

Strategy C resolves this: graph = truth, work order = adapter/UX.

### Phased Evolution Path (Design Only)

```
Phase 0 (today)
  Runtime MVP only. Graph schema exists unwired.

Phase 1 — Coexistence (Strategy A patterns)
  Optional link: work order ↔ activity instance
  Reports continue; no forced graph adoption
  Planning prototype remains client-side validation

Phase 2 — Adapter truth (Strategy C beginning)
  New graph-backed activities created from WBS + Location
  Daily Report submission writes ProgressLog on linked activity
  Work order becomes projection of linked activity for field UX

Phase 3 — Graph-primary (Strategy C mature)
  Dashboard and analytics read from Operational Graph
  Work order remains field entry surface, not authoritative store
  Lifecycle and validation become graph-aware with work-order adapter fallback

Phase 4 — Full graph (optional projects)
  Projects with full planning use graph natively
  Simple projects may still use lightweight work-order adapter only
```

### Alignment with BetavanX Identity

| Principle | How Strategy C honors it |
|-----------|--------------------------|
| Visibility platform, not ERP | Field UX stays simple |
| WBS ≠ Schedule | Graph truth separate from schedule view |
| Activity Instance = canonical | Backend truth moves to graph |
| Operational Task = UX label | Work order language preserved |
| Workforce optional | Adapter uses `reported_by` string; workforce link optional |
| Lightweight adoption | Graph depth is opt-in per project |

### What This Recommendation Does NOT Mean

- It does **not** authorize schema changes or API work
- It does **not** require immediate work order replacement
- It does **not** choose Workflow Context or Constraint designs (still open)
- It does **not** force all projects onto full graph planning

---

## SECTION 6 — Open Questions

**Status:** Open (bridge-specific — complements `open-architecture-questions.md`)

These questions must be resolved before any bridge implementation begins.

---

### 1. Activity State Ownership

**Question:** Who owns execution state — Lifecycle Engine (work order) or Activity Instance (`operational_status`)?

| Option | Implication |
|--------|-------------|
| Lifecycle remains owner; activity mirrors | Simple adapter; dual state sync |
| Activity owns state; lifecycle reads graph | Graph-primary; lifecycle refactor |
| Both with defined precedence | Needs strict sync rules |

**Status:** Open Question

---

### 2. Progress Ownership

**Question:** Is progress truth on Daily Report, ProgressLog, or ActivityInstance snapshot?

**Recommended convention (design only):**

- **ProgressLog** = append-only truth
- **ActivityInstance.progress_percent** = latest snapshot
- **Daily Report** = UX submission that creates ProgressLog via adapter

**Status:** Open Question — convention proposed, not enforced

---

### 3. Validation Ownership

**Question:** Does validation anchor on report, work order, activity, or progress log?

Today: validation runs on report + work order context.

Future options:

- Validate adapter submission before ProgressLog write
- Validate ProgressLog entries in graph context
- Maintain parallel validation paths during transition

**Status:** Open Question

---

### 4. Daily Report Future Role

**Question:** Does Daily Report remain a first-class entity or become a submission DTO only?

| Option | Implication |
|--------|-------------|
| Remain entity + link to ProgressLog | Audit trail preserved; dual storage |
| Become DTO → ProgressLog only | Simpler graph; loses report history shape |
| Report = view over ProgressLog | Single store; report is read projection |

**Status:** Open Question

---

### 5. Work Order Future Role

**Question:** Permanent field adapter or temporary migration shim?

Strategy C assumes **permanent field adapter** for lightweight projects.
Strategy B assumes **temporary shim** until full replacement.

**Status:** Open Question — leaning permanent adapter under Strategy C recommendation

---

### 6. Link Cardinality

**Question:** Is the work order ↔ activity relationship 1:1, 1:N, or N:1?

Examples:

- One work order = one activity (simple field task)
- One work order = summary of multiple activities (unlikely)
- Multiple work orders = one activity (reporting splits)

**Status:** Open Question — 1:1 is simplest for Phase 1

---

### 7. Projects Without Graph

**Question:** Can projects operate with work orders only and zero Activity Instances?

MVP philosophy suggests **yes** — graph must remain optional.

**Status:** Open Question — recommended yes

---

### 8. KPI and Analytics Source Switch

**Question:** When do KPI/analytics read from graph instead of `task_id` / `kpi_history`?

Requires defined cutover or dual-read period.

**Status:** Open Question

---

### 9. Lifecycle Blocker ↔ Constraint Mapping

**Question:** Do OperationalBlockers map to future Constraint entities on activities?

**Status:** Open Question — see also `open-architecture-questions.md` #1

---

### 10. WBS / Location Requirement for Adapter

**Question:** Must every bridged activity have WBS Template and Location Node,
or can adapter create minimal/default instances for simple field tasks?

**Status:** Open Question — affects field adoption friction

---

## Bridge Open Questions Summary

| # | Question | Status |
|---|----------|--------|
| 1 | Activity state ownership | Open |
| 2 | Progress ownership | Open |
| 3 | Validation ownership | Open |
| 4 | Daily report future role | Open |
| 5 | Work order future role | Open |
| 6 | Link cardinality | Open |
| 7 | Projects without graph | Open |
| 8 | KPI source switch | Open |
| 9 | Blocker ↔ constraint mapping | Open |
| 10 | WBS/location requirement for adapter | Open |

---

## Architecture Recommendation Summary

BetavanX should **not** replace its Runtime MVP with a big-bang graph migration.

The aligned evolution path is:

1. **Keep** Daily Work Orders and Daily Reports as the **field-facing UX layer**
2. **Introduce** Activity Instances and ProgressLogs as the **backend truth layer**
3. **Connect** the two with an explicit, optional adapter bridge
4. **Grow** graph capabilities (WBS, Location, Workflow, Dependencies) as **opt-in planning depth**
5. **Preserve** lightweight adoption — projects without graph planning remain valid

**Target bridge architecture:** Strategy C  
**First transition pattern:** Strategy A coexistence  
**Rejected for BetavanX MVP:** Strategy B full replacement

This preserves what works today while creating a credible path to the Operational
Graph Architecture defined in `core-operational-model.md` and `glossary.md`.

---

## Document Index

| Document | Role |
|----------|------|
| This document | Bridge design and migration philosophy |
| `current-vs-target-architecture.md` | Three-layer reality model |
| `audits/core-operational-foundation-audit.md` | Schema foundation audit |
| `open-architecture-questions.md` | Cross-cutting unresolved questions |
| `glossary.md` | Canonical terminology |

**No code, schema, API, or runtime changes are specified or authorized by this document.**
