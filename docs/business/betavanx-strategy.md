# BetavanX — Strategic Vision & Market Entry

**Status:** Current (business strategy — reconciled with Phase 1 product freeze)

**Related documents:**

- `docs/product/phase-1-product-definition.md` — Phase 1 scope freeze
- `docs/business/go-to-market-hypothesis.md` — GTM hypothesis
- `docs/business/business-status.md` — current business status summary
- `docs/architecture/current-vs-target-architecture.md` — technical layer reality

---

## Document Layers

This document explicitly separates three layers. Do not conflate them in sales,
product, or engineering discussions.

| Layer | Identity | Status |
|-------|----------|--------|
| **Long-Term Vision** | Building Lifecycle Intelligence Platform | Future Vision |
| **Phase 1 Product** | Operational Construction Visibility Platform | Current product scope |
| **Current Runtime MVP** | Daily work order + report visibility stack | Partial — implemented today |

---

## Long-Term Vision

**Status:** Future Vision

BetavanX long-term vision is a **Building Lifecycle Intelligence Platform**.

Mission: help buildings be designed, constructed, operated, maintained, and
improved over time — with transparency, accountability, and longer building lifespan.

**Every Building Has A BetavanX.**

Each building should possess a persistent digital identity throughout its lifecycle.

### Phase 2+ Vision Concepts

These are **not available today**. They are long-term strategic direction only.

| Concept | Description |
|---------|-------------|
| **Building Passport** | Persistent post-construction identity: warranties, inspections, maintenance, contractor history |
| **Building Memory** | Continuously growing operational history for each building |
| **Trust Network** | Market where buyers seek buildings with verified BetavanX records |

**Strategic principle (long-term):**

BetavanX enters through construction → grows through transparency → scales through trust →
ultimately becomes the lifecycle intelligence layer of buildings.

---

## The Problem

**Status:** Current

Today building information is fragmented. Critical information is often lost after construction:

- execution history
- inspections and test results
- warranties and maintenance records
- contractor and repair history

As a result: owners lack visibility, investors lack transparency, buyers lack trust,
operators lack historical knowledge.

BetavanX begins solving this during **construction** — where data originates and trust
is first established.

---

## Market Entry Strategy

**Status:** Current

BetavanX does **not** enter the market through full lifecycle management.

Market entry begins in the **construction phase** because:

- operational data is generated on site
- visibility is most urgently needed
- accountability and trust begin during execution

Phase 1 product delivers construction visibility.
Long-term lifecycle concepts are **Phase 2+ Vision** — not market-entry promises.

---

## Current Runtime MVP

**Status:** Partial (implemented today)

What BetavanX **runs in production today**:

```
Project (lightweight project_id)
    → Daily Work Orders
        → Daily Reports
            → Validation Engine
            → Lifecycle Engine
                → Dashboard Visibility
                → KPI / Progress Tracking
                → Recommendations (rule-based)
```

**Operational truth today:** Daily Reports on Daily Work Orders, enriched by validation
and lifecycle, summarized on dashboards.

**Not live in runtime:**

- Operational Graph
- Workflow Engine
- Activity Instance execution backbone
- Building Passport
- Predictive forecasting

See: `docs/architecture/current-vs-target-architecture.md`

---

## Phase 1 Product

**Status:** Current (frozen scope)

**Product identity:** **Operational Construction Visibility Platform**

Phase 1 gives construction teams a daily operational command view — work orders, field
reports, progress monitoring, and stakeholder-readable dashboards — without enterprise overhead.

### Phase 1 Core (Ship)

| Capability | Scope |
|------------|-------|
| Daily Work Orders | Primary executable unit |
| Daily Reports | Field operational truth input |
| Validation | Report trust and reliability |
| Lifecycle | Work-order state and blockers |
| Progress Tracking | Progress %, CPI, SPI, KPI trends |
| Dashboard | Operational command center |
| Investor Visibility | Read-only progress and KPI summary (see below) |
| Recommendations | Lightweight rule-based hints |

### Phase 1 Lightweight / Preview

| Capability | Boundary |
|------------|----------|
| Projects | Lightweight project context |
| WBS | Taxonomy reference — not scheduling |
| Baselines | Simple planned vs actual |
| Schedule View | Gantt visualization only — preview acceptable |

### Phase 1 Explicitly NOT

- ERP, auto-scheduling, AI forecasting
- Operational Graph runtime
- Workflow Engine (operational)
- Building Passport
- BIM / Digital Twin
- Workforce as core requirement

Canonical scope: `docs/product/phase-1-product-definition.md`

---

## Customer Structure

**Status:** Current

### Users (daily operators)

- Project Managers
- Site Supervisors
- Technical Office Teams

Goal: improve execution visibility through daily work orders and reports.

### Buyers (organizations that pay)

**Primary anchor customer:**

- **Developers relying on pre-sales** — transparency supports buyer and investor confidence

**Secondary customers:**

- **Small construction firms** — need lightweight operational visibility
- **Project owners seeking visibility** — need accountability without ERP complexity

Also relevant: construction companies, real estate investors (context-dependent).

### Ultimate Beneficiaries

- Pre-buyers and property buyers
- Building owners and operators

These groups benefit from transparency generated during construction.
Building Passport benefits are **Phase 2+ Vision**.

---

## Investor & Pre-Buyer Visibility

**Status:** Partial (Phase 1 scope defined — not fully shipped as dedicated investor portal)

One of BetavanX's key differentiators is **project transparency backed by validated field data**.

### Phase 1 Investor Visibility (In Scope)

Stakeholders can access:

- **project progress** — current progress % from operational data
- **progress trends** — KPI trend direction (CPI, SPI)
- **validated reporting** — reports processed through validation engine
- **human-readable dashboard summary** — operational status without training

### Phase 1 Investor Visibility (NOT In Scope)

Do not imply these exist today:

- ~~completion forecasts~~ → **Future Capability**
- ~~predictive forecasting~~ → **Future Capability**
- ~~construction evidence engine~~ → **Future Capability**
- ~~milestone achievement engine~~ → **Future Capability** (manual milestones via work orders only)
- ~~Building Passport access~~ → **Phase 2+ Vision**

**Phase 1 value:** trusted visibility from daily operational data — not predictive analytics.

---

## Distribution Strategy

**Status:** Current

**Phase 1 adoption path:**

Construction Visibility (daily reporting + dashboard)
→ stakeholder trust from validated progress data
→ stronger pre-sales credibility for developers
→ broader adoption among small teams and project owners

**Phase 2+ Vision expansion path:**

More building records → Building Passport → Building Memory → Trust Network

The long-term flywheel depends on Phase 1 data quality first.
Poor field data destroys trust before any lifecycle vision can compound.

---

## Strategic Principles

| Principle | Phase 1 expression | Long-term expression |
|-----------|-------------------|---------------------|
| Enter through construction | Daily work orders + reports | Construction history as building record seed |
| Grow through transparency | Validated dashboards | Stakeholder and buyer trust |
| Scale through trust | Reliable operational reporting | Building Passport and Trust Network |
| Lifecycle intelligence | **Not Phase 1** | **Phase 2+ Vision** |

---

## Document Index

| Document | Role |
|----------|------|
| This document | Strategic vision and market entry |
| `go-to-market-hypothesis.md` | GTM hypothesis and flywheel |
| `business-status.md` | Current business status summary |
| `../product/phase-1-product-definition.md` | Phase 1 product freeze |
