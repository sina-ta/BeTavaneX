# BetavanX — Go-To-Market Hypothesis

**Status:** Current (strategic hypothesis — reconciled with Phase 1 product freeze)

**Last Updated:** May 2026

**Related documents:**

- `betavanx-strategy.md`
- `business-status.md`
- `docs/product/phase-1-product-definition.md`
- `docs/architecture/current-vs-target-architecture.md`

---

## Purpose

This document defines the current market-entry hypothesis for BetavanX.

It does not define architecture or implementation.

It defines:

- who pays
- who uses
- who benefits
- how adoption may spread
- how BetavanX may become an industry standard over time

---

## Document Layers

| Layer | What it is | Status |
|-------|------------|--------|
| **Long-Term Vision** | Building Lifecycle Intelligence Platform | Future Vision |
| **Phase 1 Product** | Operational Construction Visibility Platform | Current scope |
| **Current Runtime MVP** | Work orders, reports, validation, dashboard | Partial |

---

## Long-Term Vision

**Status:** Future Vision

BetavanX long-term vision is a **Building Lifecycle Intelligence Platform**.

**Every Building Has A BetavanX** — a persistent digital identity from construction
through operation, containing construction history, inspections, warranties, maintenance,
repair history, and operational intelligence.

BetavanX ultimately creates value through **Trust** — not merely project management.

This vision spans the full building lifecycle. It is **not** the Phase 1 product promise.

---

## Strategic Insight

**Status:** Current

BetavanX does not ultimately create value through project management alone.

BetavanX creates value through **Trust** — verified operational transparency that
stakeholders can rely on.

Phase 1 begins trust creation through **validated construction visibility**.
Long-term trust infrastructure (Building Passport, Trust Network) is **Phase 2+ Vision**.

---

## Market Entry Reality

**Status:** Current

Market entry must begin where:

- data is generated
- visibility is needed
- accountability matters
- trust begins

That point is **construction** — specifically daily field execution and reporting.

BetavanX does not enter through lifecycle management, building passports, or trust networks.
Those are downstream outcomes of reliable construction-phase data.

---

## Current Runtime MVP

**Status:** Partial (what exists in production today)

```
Daily Work Orders → Daily Reports → Validation → Dashboard Visibility
```

Supporting engines already active: Lifecycle, KPI aggregation, rule-based Recommendations.

**Operational truth:** report-driven, work-order-centric.

**Not operational today:**

- Workflow Engine
- Operational Graph
- Activity Instance backbone
- Predictive forecasting
- Building Passport

---

## Phase 1 Market Entry

**Status:** Current (frozen product scope)

**Product identity:** Operational Construction Visibility Platform

**Objective:** Create trusted construction transparency through daily operational data.

### Phase 1 Core Capabilities (Ship)

| Capability | Phase 1 role |
|------------|--------------|
| Daily Work Orders | Issue and track executable work |
| Daily Reports | Capture field operational truth |
| Validation | Trust layer on reporting reliability |
| Progress Tracking | Progress %, CPI, SPI from operational data |
| Dashboards | Operational command center visibility |
| Investor Visibility | Read-only progress and KPI summary for stakeholders |

### Phase 1 Lightweight / Preview

| Capability | Boundary |
|------------|----------|
| Project Visibility | Lightweight project context |
| WBS | Taxonomy reference — optional, not required for daily reporting |
| Schedule View | Visualization only — preview acceptable |

### Phase 1 NOT Promised

- Workflow-based execution engine
- Operational Graph
- Completion forecasts / predictive analytics
- Construction evidence engine
- Building Passport
- Auto-scheduling / CPM

Canonical reference: `docs/product/phase-1-product-definition.md`

---

## Customer Structure

**Status:** Current

### Users

Daily operational users:

- Project Managers
- Site Supervisors
- Technical Office Teams
- Construction Coordinators

Goal: improve execution visibility through work orders and daily reports.

### Buyers

Organizations that purchase the platform.

**Primary anchor customer:**

- **Developers relying on pre-sales** — construction transparency directly supports
  buyer confidence and project credibility during sales

**Secondary customers:**

- **Small construction firms** — need operational visibility without ERP overhead
- **Project owners seeking visibility** — need accountability and stakeholder reporting

Also relevant: construction companies, real estate investors.

### Ultimate Beneficiaries

- Pre-buyers and property buyers
- Building owners and operators

Benefit from transparency during construction.
Long-term Building Passport benefits are **Phase 2+ Vision**.

---

## Pre-Sales Transparency Hypothesis

**Status:** Current (hypothesis — Phase 1 enables partial validation)

Traditional pre-sales rely on promises, brochures, and periodic updates.
Buyers have limited visibility into actual construction progress.

BetavanX Phase 1 hypothesis: **validated operational visibility increases buyer trust.**

### Phase 1 — What Pre-Buyers Can Access (In Scope)

- current project progress from operational data
- progress trends (KPI direction — CPI, SPI)
- validated daily reporting summary
- human-readable dashboard status

### Phase 1 — What Pre-Buyers Cannot Access (Not In Scope)

| Claim | Status |
|-------|--------|
| Completion forecasts | **Future Capability** |
| Predictive milestone dates | **Future Capability** |
| Construction evidence gallery / media engine | **Future Capability** |
| Verified building passport | **Phase 2+ Vision** |

**Critical dependency:** trust requires **data quality**. Validation engine is Phase 1
differentiator — poor reporting destroys the pre-sales hypothesis.

---

## Value Proposition For Developers (Primary Anchor)

**Status:** Current (hypothesis)

BetavanX may help developers who rely on pre-sales:

- improve project credibility with validated progress data
- improve investor and buyer confidence
- reduce information asymmetry between developer and buyer
- increase transparency without enterprise PMO overhead

**Phase 1 outcome (realistic):** stronger operational reporting discipline and
stakeholder-readable status — not automated sales acceleration.

**Phase 2+ outcome (hypothesis):** faster pre-sales through compounding trust records.

---

## Visibility Flywheel

**Status:** Partial (Phase 1 enables first stage only)

```
Phase 1 (Current):
  Construction Visibility
      ↓
  Validated Reporting
      ↓
  Stakeholder Trust

Phase 2+ Vision (Future):
  Stronger Pre-Sales
      ↓
  More Projects Using BetavanX
      ↓
  Building Records Accumulation
      ↓
  Building Passport
      ↓
  Building Memory
      ↓
  Industry Trust Network
```

Phase 1 must prove the first two stages before the flywheel can compound.
Do not pitch the full flywheel as current product capability.

---

## Phase 2+ Vision Concepts

**Status:** Future Vision — not Phase 1 commitments

### Building Passport Evolution

After project completion, BetavanX may evolve into a building passport containing
warranties, insurance, equipment records, maintenance history, and inspection records.

**Not available today.**

### Building Memory Evolution

Building Passports may accumulate operational history over time.

**Not available today.**

### Trust Network Hypothesis

Long-term: buyers seek buildings with verified BetavanX records.

**"Does this building have BetavanX?"** — Phase 2+ market education goal, not current reality.

---

## Strategic Assumptions

**Status:** Current (hypotheses to validate)

1. Construction transparency creates measurable value for developers and owners
2. Developers relying on pre-sales benefit from validated progress visibility
3. Pre-buyers value real operational data over marketing-only updates
4. Data quality (validation) is prerequisite for trust — not optional
5. Building records become more valuable over time (**Phase 2+ assumption**)
6. Trust compounds through accumulated historical data (**long-horizon assumption**)

Assumptions 5–6 require Phase 1 data quality success first.

---

## Major Risks

**Status:** Current

| Risk | Detail |
|------|--------|
| **Adoption Risk** | Developers may resist operational transparency that exposes delays |
| **Data Quality Risk** | Trust requires reliable field reporting — poor data destroys value |
| **Over-Promise Risk** | Pitching forecasting, workflow engine, or Building Passport before Phase 1 delivery |
| **Market Education Risk** | Market may not understand validated visibility vs generic PM tools |
| **Long Horizon Risk** | Trust Network requires years of adoption — cannot be Phase 1 sales promise |
| **Segment Confusion Risk** | Primary (pre-sales developers) vs secondary (small builders) need different messaging |

---

## Strategic Principle

**Status:** Current

| Stage | Principle |
|-------|-----------|
| **Phase 1** | Enter through construction visibility |
| **Phase 1** | Grow through validated transparency |
| **Phase 1** | Create trust through reliable daily reporting |
| **Phase 2+** | Scale through accumulated building intelligence |

---

## Long-Term Goal

**Status:** Future Vision

BetavanX becomes the trusted operational memory of buildings — not merely construction
software or project management, but a persistent intelligence and trust layer across
the entire building lifecycle.

**Phase 1 is the first step:** prove construction visibility and reporting trust.
Everything else depends on that foundation.

---

## Document Index

| Document | Role |
|----------|------|
| This document | GTM hypothesis |
| `betavanx-strategy.md` | Strategic vision |
| `business-status.md` | Current status summary |
| `../product/phase-1-product-definition.md` | Phase 1 scope freeze |
