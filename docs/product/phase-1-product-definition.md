# BetavanX — Phase 1 Product Definition

**Status:** Frozen (product scope — documentation only)

**Effective purpose:** Define exactly what BetavanX Phase 1 is — and is not —
to prevent architecture drift and feature creep at market entry.

**Related architecture (do not redefine here):**

- `docs/architecture/current-vs-target-architecture.md`
- `docs/architecture/glossary.md`
- `docs/architecture/runtime-to-operational-graph-bridge.md`
- `docs/architecture/core-platform-diagram.md`

**Constraint:** This document defines **product scope only**. It does not authorize
new features, schema, APIs, or engines.

---

## SECTION 1 — Product Identity

### BetavanX Is

**Operational Construction Visibility Platform**

A lightweight platform for construction teams to:

- issue and track daily work
- capture field reports
- monitor progress and operational health
- share project status with stakeholders

BetavanX helps teams **see what is happening on site** — not run enterprise back-office operations.

### BetavanX Is NOT

| Category | Phase 1 stance |
|----------|----------------|
| **ERP** | Not a general enterprise resource system |
| **Scheduling Software** | Not a CPM / auto-scheduling product |
| **Resource Optimization Platform** | Not crew/equipment optimization engine |
| **Digital Twin** | Not a BIM or 4D twin platform |
| **Construction AI Platform** | Not an AI-first autonomous planning product |

### Phase 1 Product Statement

> BetavanX Phase 1 gives small construction teams a **daily operational command view**:
> work orders, field reports, progress, and dashboards — with enough planning context
> to stay organized, without enterprise overhead.

---

## SECTION 2 — Target Customer

### Primary Customer (Phase 1)

| Segment | Why BetavanX fits |
|---------|-------------------|
| **Small builders** | Need visibility without ERP complexity |
| **Owner-builders** | Need progress transparency and simple reporting |
| **Project managers** | Need daily execution tracking and status roll-up |
| **Small construction teams** | Field-friendly work orders and reports |
| **Investor-facing projects** | Need readable status for stakeholders |

Typical project size: **single site to small multi-phase building projects**
where daily reporting and progress visibility matter more than enterprise planning bureaucracy.

### Explicitly NOT Phase 1 Target

| Segment | Reason excluded |
|---------|-----------------|
| **Enterprise EPC** | Requires procurement, workforce, equipment, PMO depth |
| **Mega projects** | Requires multi-contractor orchestration at scale |
| **Government PMO systems** | Requires compliance, procurement, and enterprise workflow depth |

Phase 1 optimizes for **adoption speed and operational clarity**, not enterprise breadth.

---

## SECTION 3 — Phase 1 Core Features

Only features **required for market entry** are in scope.

Legend:

- **Ship** — required for Phase 1 complete
- **Lightweight** — included in minimal, non-enterprise form
- **Preview** — visible but not production-critical; must not block launch

### Core Execution Loop (Ship)

| Feature | Phase 1 scope |
|---------|---------------|
| **Work Orders** | Daily work orders as primary executable unit (`task_id`). Create, list, assign label, priority, status. |
| **Daily Reports** | Field submission: actual qty, manpower count, equipment hours, material usage, delay note, reporter name. |
| **Progress Tracking** | Progress %, CPI, SPI, KPI trends derived from reports and work orders. |
| **Validation** | Report trust pipeline — anomaly detection and reliability scoring on submissions. |
| **Lifecycle** | Work-order execution state and operational blockers (lightweight, not full graph constraint engine). |

### Visibility Layer (Ship)

| Feature | Phase 1 scope |
|---------|---------------|
| **Dashboard** | Operational overview: KPI strip, work order status, trends, operational summary. |
| **Task Detail** | Single work-unit view: progress, reports, recommendations, lifecycle placeholder. |
| **Performance View** | KPI trends and analytics indicators (not advanced forecasting). |
| **Investor Visibility** | Read-only project status summary suitable for stakeholders — dashboard-derived, human-readable. |

### Project Context (Lightweight)

| Feature | Phase 1 scope |
|---------|---------------|
| **Projects** | Lightweight project context (`project_id`). Single active project acceptable for v1 launch; multi-project support lightweight. |
| **Not required:** full `core_operational.Project` graph container at runtime. |

### Planning Context (Lightweight / Preview)

| Feature | Phase 1 scope | Boundary |
|---------|---------------|----------|
| **WBS** | Construction taxonomy reference — template browsing by phase for work categorization. | **Not** a scheduling engine. **Not** mandatory for daily reporting. |
| **Baselines** | Simple planned vs actual on work orders and KPI (manual baseline, not CPM baseline). | **Not** enterprise baseline management. |
| **Schedule View** | Lightweight Gantt-style visualization (drag dates, simple dependencies). | **Visualization only.** **Not** auto-scheduling. **Preview** acceptable if client-side prototype. |

### Resource Tracking (Lightweight)

| Feature | Phase 1 scope |
|---------|---------------|
| **Basic Resource Tracking** | Manpower, equipment hours, and material usage **as report fields only**. |
| **Not included:** resource allocation engine, capacity planning, or workforce system. |

### Operational Support (Ship — already in runtime)

| Feature | Phase 1 scope |
|---------|---------------|
| **Recommendations** | Lightweight operational suggestions on dashboard/task detail — rule-based hints, not AI platform. |

### Phase 1 Core Feature Summary

```
Project (lightweight)
    → Work Orders
        → Daily Reports
            → Validation
            → Lifecycle
                → Progress / KPI
                    → Dashboard
                    → Investor Visibility

Optional planning context (lightweight / preview):
    WBS templates · simple baselines · schedule view (visualization only)
```

---

## SECTION 4 — Explicitly Excluded from Phase 1

These are **intentionally out of scope**. They must not be added to Phase 1
roadmap commitments without a Phase 2 review.

### Enterprise & Extension Systems

| Feature | Status |
|---------|--------|
| Workforce Engine | **Excluded** (optional extension — frozen out of Phase 1 core) |
| Equipment Management | **Excluded** |
| Procurement Management | **Excluded** |
| Inventory Management | **Excluded** |
| Marketplace | **Excluded** |

### Advanced Technology

| Feature | Status |
|---------|--------|
| BIM Integration | **Excluded** |
| Digital Twin / 4D BIM Viewer | **Excluded** (placeholder UI not a Phase 1 promise) |
| AI Forecasting | **Excluded** |
| Automatic Scheduling / CPM Engine | **Excluded** |
| Operational Graph Runtime | **Excluded** (schema foundation exists — not Phase 1 product) |
| Graph Mutation / Optimization Engines | **Excluded** |

### Platform Depth Not Required for Market Entry

| Feature | Status |
|---------|--------|
| Document Storage / DMS | **Excluded** |
| Full multi-project enterprise PMO | **Excluded** |
| Contract / cost accounting ERP | **Excluded** |
| Advanced workforce intelligence (fatigue, reliability scoring) | **Excluded** |
| Real-time websocket field sync | **Excluded** |
| Full localization / multi-language product (beyond foundation) | **Excluded** |

### Rule

If a feature is not listed in **Section 3**, it is **not Phase 1** unless explicitly
approved through a Phase 2 scope review.

---

## SECTION 5 — Differentiators

Why BetavanX Phase 1 is different from generic PM or scheduling tools:

| Differentiator | Phase 1 expression |
|----------------|-------------------|
| **Operational visibility first** | Built around daily work orders and field reports — not static Gantt plans |
| **Project transparency** | Dashboard and investor-readable status without enterprise reporting tools |
| **Construction-native workflow** | Work orders, daily reports, CPI/SPI language operators understand |
| **Human-readable dashboards** | Operational command center — not academic enterprise KPI walls |
| **Lightweight adoption** | Usable by small teams without HR, procurement, or BIM setup |
| **Report trust layer** | Validation engine improves reporting reliability — uncommon in simple tools |
| **Location-aware vision (foundation)** | Architecture supports location-aware execution; Phase 1 exposes via planning preview, not full graph |
| **Honest scope** | Does not pretend to be ERP, AI, or auto-scheduling |

**Phase 1 positioning:** *"See your site clearly every day"* — not *"Run your entire construction enterprise."*

---

## SECTION 6 — Success Criteria

Phase 1 is **complete for market entry** when all of the following are true:

### Execution Loop

- [ ] A project context can be established (at minimum: active project identifier)
- [ ] Work orders can be created and listed
- [ ] Daily reports can be submitted against work orders
- [ ] Reports pass through validation and appear in reporting views
- [ ] Work-order lifecycle state is visible (including blockers where applicable)

### Visibility

- [ ] Dashboard reflects current operational reality from live data (not static JSON)
- [ ] Progress, CPI, and SPI are visible and update from report activity
- [ ] Task detail view shows work-unit intelligence (progress, reports, status)
- [ ] Performance view shows KPI trends

### Stakeholder Value

- [ ] An investor or owner can view a human-readable project status summary
  without needing training on construction software

### Quality Bar

- [ ] Application builds and runs without workforce extension enabled
- [ ] Core workflows function independently of optional extensions
- [ ] Product UX does not require WBS, schedule, or graph setup to use daily reporting

### Explicit Non-Requirements for Phase 1 Complete

Phase 1 completion does **not** require:

- Operational Graph wired to runtime
- Auto-scheduling or CPM
- BIM viewer connected
- Workforce module enabled
- Document management
- Multi-language full product translation

---

## SECTION 7 — Phase 2 Candidates

Future possibilities — **not Phase 1 commitments**.

Move ideas here when they appear in discussions to prevent scope creep.

### Extensions & Enterprise Depth

- Workforce extension (attendance, crew, optional intelligence)
- Equipment management
- Procurement and inventory
- Contract and cost modules

### Planning & Graph

- Operational Graph runtime (Activity Instance as truth layer)
- Runtime ↔ graph bridge (adapter implementation)
- Full location-aware activity instantiation
- Workflow graph engine (branching suggestions → enforced paths)
- Reactive scheduling and replanning
- Advanced planning backend (replace client-side prototype)

### Intelligence & Integration

- Recommendation engine (graph-aware)
- AI-assisted forecasting and delay prediction
- BIM / 4D integration
- Digital twin visualization
- Advanced analytics and risk heatmaps (beyond placeholder)

### Platform

- Full project entity and multi-project management
- Document storage and drawing links
- Full Persian/English operational product localization
- Mobile-native field app
- Marketplace / subcontractor network

### Rule

Phase 2 items require a **new product scope review** before becoming commitments.
Architecture docs may describe future direction; this section does not approve building it.

---

## Scope Guardrails

Use this document to reject scope creep:

| Question | If "no" → defer to Phase 2 |
|----------|---------------------------|
| Is it required for daily work order + report + dashboard loop? | |
| Can a small team use BetavanX without this on day one? | |
| Does it require a new engine or enterprise module? | |
| Is it already excluded in Section 4? | |

**Default answer for new feature requests during Phase 1:** *"Phase 2 candidate
unless it directly completes a Section 6 success criterion."*

---

## Document Index

| Document | Role |
|----------|------|
| This document | Phase 1 product scope freeze |
| `docs/architecture/current-vs-target-architecture.md` | Technical layer reality |
| `docs/architecture/runtime-to-operational-graph-bridge.md` | Future evolution path |
| `docs/product/phase-1-product-definition.md` | Phase 1 product scope (this document) |

---

## Freeze Statement

**BetavanX Phase 1 = Operational Construction Visibility Platform**

Ship daily execution visibility for small construction teams.
Defer enterprise depth, graph runtime, and AI to Phase 2.

No architecture changes are implied by this document.
Product scope is frozen; implementation must align to Sections 3, 4, and 6.
