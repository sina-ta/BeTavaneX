# BetavanX — Core Platform Diagram

**Status:** Implemented (documentation)

Aligned with current runtime reality as of the documentation reconciliation sprint.
See `current-vs-target-architecture.md` for layer definitions.

---

## Core Runtime

**Status:** Implemented

BetavanX Core (production today):

```
BetavanX Core
│
├── Projects
├── Daily Work Orders
├── Daily Reports
├── Dashboard
├── KPI Engine
├── Validation Engine
├── Lifecycle Engine
└── Recommendations
```

These components are active in `backend/api.py` and current frontend dashboard flows.
Validation, Lifecycle, and Recommendations are **core runtime engines** — not optional extensions.

---

## Operational Foundation

**Status:** Implemented (foundation) — not wired to runtime

Schema and architecture foundation for the target Operational Graph:

```
Operational Foundation
│
├── WBS Templates
├── Workflow Graph
├── Location Graph
└── Activity Instances
```

Package: `backend/core_operational/`

Entities exist as models and schemas.
They are not yet registered, migrated, or exposed through runtime APIs.

---

## Schedule View

**Status:** Prototype

BetavanX does **not** treat Schedule as a core system pillar.

```
Schedule View (visualization only)
│
└── Gantt View
```

**Rule:** Gantt is visualization only.

Schedule arrangement is a temporary view over operational graph state —
not the execution engine itself.

Current Gantt exists only in the `/dashboard/planning` prototype (localStorage).

---

## Optional Extensions

**Status:** Partial

```
Optional Extensions
│
├── Workforce
├── Equipment
├── Procurement
├── BIM
└── Future Extensions
```

Only **Workforce** is implemented today as an env-gated extension:

- `BETAVANX_ENABLE_WORKFORCE_EXTENSION`
- `NEXT_PUBLIC_ENABLE_WORKFORCE_EXTENSION` (frontend)

Equipment, Procurement, and BIM are architectural placeholders — not runtime modules yet.

---

## Layer Relationship

```
┌─────────────────────────────────────┐
│         Core Runtime (live)         │
│  Work Orders · Reports · Dashboard  │
│  KPI · Validation · Lifecycle       │
└─────────────────────────────────────┘
                  │
                  │ reads operational data
                  ▼
┌─────────────────────────────────────┐
│    Operational Foundation (schema)  │
│  WBS · Workflow · Location · Activity│
└─────────────────────────────────────┘
                  │
                  │ target integration
                  ▼
┌─────────────────────────────────────┐
│      Target Operational Graph       │
│   full graph execution model        │
└─────────────────────────────────────┘
                  │
                  │ visualized by
                  ▼
┌─────────────────────────────────────┐
│         Schedule View / Gantt       │
│      visualization layer only       │
└─────────────────────────────────────┘
```

---

## Related Documents

- `current-vs-target-architecture.md`
- `glossary.md`
- `operational-capability-model.md`
