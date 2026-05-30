# BetavanX — Business Status

**Status:** Current (living summary — reconciled May 2026)

Single reference for business, product, and runtime alignment.
Updated during business documentation reconciliation sprint.

---

## Current Runtime MVP

**Status:** Partial (implemented — production today)

| Component | State |
|-----------|-------|
| Daily Work Orders | Implemented |
| Daily Reports | Implemented |
| Validation Engine | Implemented |
| Lifecycle Engine | Implemented |
| Dashboard Visibility | Implemented |
| KPI / Progress Tracking | Implemented |
| Recommendations | Implemented (rule-based) |
| Projects | Partial (lightweight `project_id`) |
| Workforce Extension | Optional — not core |

**Operational truth:** Daily Reports on Daily Work Orders → Validation → Dashboard

**Not in runtime:**

- Operational Graph
- Workflow Engine
- Activity Instance backbone
- Predictive forecasting
- Building Passport
- Dedicated investor portal

Reference: `docs/architecture/current-vs-target-architecture.md`

---

## Phase 1 Product Scope

**Status:** Current (frozen)

**Identity:** Operational Construction Visibility Platform

**Ship:**

- Work Orders, Daily Reports, Validation, Lifecycle
- Progress Tracking (CPI, SPI, progress %)
- Dashboard, Task Detail, Performance View
- Investor Visibility (read-only progress + KPI summary)
- Lightweight Recommendations

**Lightweight / Preview:**

- Projects, WBS taxonomy browse, simple baselines, Schedule View (visualization only)

**Excluded from Phase 1:**

- ERP, auto-scheduling, AI forecasting, Operational Graph runtime
- Workflow Engine, Building Passport, BIM, workforce as core
- Document storage, marketplace, enterprise PMO

Reference: `docs/product/phase-1-product-definition.md`

---

## Long-Term Vision

**Status:** Future Vision

**Identity:** Building Lifecycle Intelligence Platform

**Every Building Has A BetavanX.**

| Concept | Status |
|---------|--------|
| Building Passport | Phase 2+ Vision |
| Building Memory | Phase 2+ Vision |
| Trust Network | Phase 2+ Vision |
| Lifecycle intelligence (design → operate → maintain) | Phase 2+ Vision |

Phase 1 seeds construction-phase data that may later feed lifecycle records.
Lifecycle vision is **not** a Phase 1 sales promise.

Reference: `docs/business/betavanx-strategy.md`

---

## Current GTM Hypothesis

**Status:** Current (hypothesis — partially testable in Phase 1)

### Primary Anchor Customer

**Developers relying on pre-sales**

Construction transparency backed by validated reporting supports buyer and investor
confidence during project sales.

### Secondary Customers

- Small construction firms needing operational visibility
- Project owners seeking accountability without ERP complexity

### Value Chain

| Role | Phase 1 value |
|------|---------------|
| **Users** (PM, site supervisors) | Daily execution visibility |
| **Buyers** (developers, owners) | Stakeholder transparency |
| **Beneficiaries** (pre-buyers, investors) | Progress and KPI visibility |

### Phase 1 Flywheel (Testable Now)

```
Daily Reporting → Validation → Trusted Dashboard → Stakeholder Confidence
```

### Phase 2+ Flywheel (Hypothesis — Not Current Product)

```
Pre-Sales Lift → More Projects → Building Records → Passport → Trust Network
```

Reference: `docs/business/go-to-market-hypothesis.md`

---

## Investor Visibility — Phase 1 Definition

**Status:** Partial (scope defined — dedicated portal not yet shipped)

### In Scope (Phase 1)

- Progress visibility from operational data
- KPI trends (CPI, SPI direction)
- Validated reporting summary
- Human-readable dashboard-derived status

### NOT In Scope (Do Not Pitch as Phase 1)

| Capability | Label |
|------------|-------|
| Completion forecasts | Future Capability |
| Predictive analytics | Future Capability |
| Construction evidence engine | Future Capability |
| Building Passport access | Phase 2+ Vision |

---

## Current Risks

**Status:** Current

| Risk | Impact |
|------|--------|
| **Adoption resistance** | Developers may avoid transparency that exposes delays |
| **Data quality** | Poor field reporting destroys trust value proposition |
| **Over-promise in sales** | Pitching graph, forecasting, or passport before delivery |
| **Segment confusion** | Primary (pre-sales developers) vs secondary (small builders) messaging |
| **Market education** | Buyers may not distinguish validated visibility from generic PM |
| **Architecture drift** | Building graph features before Phase 1 loop is proven |
| **Long horizon** | Trust Network requires years — cannot be near-term revenue driver |

---

## Open Business Questions

**Status:** Current (unresolved — documentation only)

| # | Question | Notes |
|---|----------|-------|
| 1 | **Primary vs secondary customer priority** | Pre-sales developers vs small builders — which gets first GTM focus? |
| 2 | **Investor portal form** | Dedicated read-only view vs shared dashboard link? |
| 3 | **Pricing model** | Per project, per seat, per developer portfolio? |
| 4 | **Pre-sales ROI proof** | What metric validates the transparency hypothesis? |
| 5 | **Iran vs international market** | Primary geography and regulatory context? |
| 6 | **Validation as sales differentiator** | How prominently to pitch trust engine vs simple visibility? |
| 7 | **Phase 1 complete definition** | Which Section 6 success criteria from product freeze block launch? |
| 8 | **Building Passport trigger** | What construction data minimum justifies Phase 2 passport pitch? |
| 9 | **Partner channel** | Sell direct to developers or through construction consultants? |
| 10 | **Competitive positioning** | vs generic PM tools (Asana, MS Project) vs construction ERP? |

Related architecture open questions: `docs/architecture/open-architecture-questions.md`

---

## Alignment Matrix

| Topic | Business | Product Freeze | Architecture | Runtime |
|-------|----------|----------------|--------------|---------|
| Phase 1 identity | Visibility Platform | Visibility Platform | Runtime MVP layer | Work orders + reports |
| Long-term identity | Lifecycle Intelligence | Phase 2+ | Target Graph | Not wired |
| Investor visibility | Progress + KPI + validation | Dashboard-derived | N/A | Dashboard exists |
| Forecasting | Future Capability | Excluded | N/A | Not implemented |
| Workflow engine | Not Phase 1 | Preview/excluded | Target | Not live |
| Building Passport | Phase 2+ Vision | Excluded | N/A | Not exists |
| Anchor customer | Developers (pre-sales) | Small builders + developers | N/A | N/A |

---

## Document Index

| Document | Role |
|----------|------|
| This document | Business status summary |
| `betavanx-strategy.md` | Strategic vision and market entry |
| `go-to-market-hypothesis.md` | GTM hypothesis and flywheel |
| `../product/phase-1-product-definition.md` | Phase 1 product freeze |
| `../architecture/current-vs-target-architecture.md` | Technical reality |
| `../architecture/runtime-to-operational-graph-bridge.md` | Future evolution path |

---

## Reconciliation Statement

Business documentation is aligned with:

- Phase 1 Product Definition (frozen)
- Architecture reconciliation (current vs target)
- Runtime MVP reality (work-order-centric)

**Default rule for new business claims:** if not in Phase 1 Product Definition Section 3,
label as **Future Capability** or **Phase 2+ Vision**.
