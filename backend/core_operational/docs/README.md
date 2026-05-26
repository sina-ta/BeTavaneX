# BetavanX Core Operational Schema Foundation

## Purpose

This package defines the foundational operational data schema for
BetavanX.

It exists to transform the operational architecture into a lightweight,
future-ready data model that can later support:

- graph-based workflows
- reactive scheduling
- activity instantiation
- location-aware execution
- operational monitoring
- progress-driven control

without implementing the scheduling engine itself yet.

---

## Package Structure

```text
backend/core_operational/
├── models/
├── schemas/
├── enums/
├── relationships/
└── docs/
```

### models/

Contains the foundational SQLAlchemy entities:

- Project
- WbsTemplate
- LocationNode
- WorkflowNode
- WorkflowEdge
- ActivityInstance
- Dependency
- Resource
- Assignment
- ProgressLog

### schemas/

Contains lightweight Pydantic schemas for the same entities so API and
service layers can adopt the operational model later without first
building the full engine.

### enums/

Contains the lightweight operational enum vocabulary used by the
foundation, such as:

- project type
- location node type
- workflow node type
- workflow edge type
- activity status
- dependency type
- resource type

### relationships/

Contains conceptual relationship definitions that document how the core
entities connect.

This is intentionally explicit because BetavanX is being built as an
operational graph foundation rather than a simple WBS-to-Gantt tool.

---

## Core Formula

The central executable concept is:

`WbsTemplate + LocationNode + Workflow Context = ActivityInstance`

This is the key architectural move that separates:

- construction taxonomy
- execution geography
- workflow possibilities
- real executable work

---

## Important Boundary

This package does **not** implement:

- schedule rendering
- Gantt logic
- optimization
- forecasting
- AI planning
- real-time updates
- advanced sequencing engines

It only establishes the foundational data structure required for those
systems to be added later without redesigning the core architecture.

---

## Why This Matters

BetavanX should not be modeled as:

`WBS -> static sequence -> schedule`

It should be modeled as:

`WBS Templates + Location Tree + Workflow Graph + Operational Reality`

which makes future dynamic planning and reactive scheduling structurally
possible.
