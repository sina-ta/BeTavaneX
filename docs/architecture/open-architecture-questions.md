# BetavanX — Open Architecture Questions

**Status:** Partial (living document)

Unresolved architecture questions that are intentionally **not decided yet**.
This document records gaps without introducing new features or redesign.

---

## 1. Constraint Entity

**Status:** Open Question

### Current State

- Lifecycle **Operational Blockers** exist on work-order-centric execution
- Constraint is defined conceptually in execution logic and operational rules docs
- No dedicated `Constraint` entity exists in `backend/core_operational/`

### Question

Should BetavanX introduce a dedicated **Constraint** entity in the Operational Graph,
or continue using lifecycle blockers as the interim constraint mechanism?

### Options (Not Decided)

| Approach | Implication |
|----------|-------------|
| Lifecycle blockers only | Simpler; work-order-centric |
| Dedicated Constraint entity | Graph-native; activity-level blocking |

### Related Documents

- `glossary.md` — Constraint
- `operational-rules.md`
- `construction-execution-logic-model.md`

---

## 2. Workflow Context

**Status:** Open Question

### Current Formula

```
WBS Template + Location + Workflow Context = Activity Instance
```

### Current State

- `ActivityInstance` has optional `workflow_node_id`
- **Workflow Context** is not formally defined as a single modeled concept
- Unclear whether context means: selected node, active edge, planner path state,
  or traversal history

### Question

What exactly constitutes **Workflow Context** at instantiation time,
and how should it be stored?

### Related Documents

- `glossary.md` — Workflow Context
- `core-operational-model.md`
- `workflow-graph.md`

---

## 3. WBS Library Scope

**Status:** Open Question

### Current Tension

| View | Source |
|------|--------|
| Global construction taxonomy library | `wbs-template-library.md` |
| Project-scoped templates | `WbsTemplate.project_id` in schema |

### Question

Is the WBS catalog a **global library** copied into projects,
or are templates **owned per project** from creation?

### Options (Not Decided)

| Approach | Implication |
|----------|-------------|
| Global library + project copy | Seed from taxonomy; project owns instances |
| Project-only templates | No shared global catalog in data model |
| Hybrid | Library IDs reference global templates |

### Related Documents

- `wbs-template-library.md`
- `backend/core_operational/models/entities.py`

---

## 4. Assignment Model Alignment

**Status:** Open Question

### Current State

Two assignment concepts exist:

| Model | Package | Meaning |
|-------|---------|---------|
| `Assignment` | `core_operational` | Resource → Activity Instance |
| Workforce assignment | `backend/workforce/` | Worker / crew → work |

Workforce is an optional extension.
Core operational assignment is schema-only and unwired.

### Question

How should core `Assignment` and workforce assignment integrate
without recreating mandatory workforce coupling?

### Related Documents

- `glossary.md`
- `current-vs-target-architecture.md`
- `operational-capability-model.md`

---

## 5. Runtime Bridge — Daily Work Order ↔ Activity Instance

**Status:** Open Question

### Current State

- Production execution uses **Daily Work Order** (`task_id`)
- Target graph uses **Activity Instance**
- No documented adapter or migration path exists

### Question

Is Daily Work Order a permanent field-reporting surface with optional graph linkage,
or a legacy entity to be replaced by Activity Instance?

### Related Documents

- `current-vs-target-architecture.md`
- `glossary.md`

---

## Summary Table

| # | Question | Status |
|---|----------|--------|
| 1 | Constraint Entity | Open Question |
| 2 | Workflow Context | Open Question |
| 3 | WBS Library Scope | Open Question |
| 4 | Assignment Model Alignment | Open Question |
| 5 | Work Order ↔ Activity Instance bridge | Open Question |

When any question is resolved, update this document and the canonical glossary.
Do not resolve these questions through documentation alone — implementation
decisions require explicit engineering work outside this reconciliation sprint.
