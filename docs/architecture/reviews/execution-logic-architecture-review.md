# BetavanX — Execution Logic Architecture Review

**Status:** Partial (review document — updated after reconciliation sprint)

**Review date context:** Updated to reflect that Lifecycle and Recommendation engines
exist in runtime MVP but are **not yet integrated into the Operational Graph**.

See: `current-vs-target-architecture.md`, `glossary.md`

---

# Architectural Assessment

The current Construction Execution Logic Model is:

# structurally strong

because it successfully separates:

* WBS
* workflow
* dependencies
* constraints
* scheduling
* execution state

This separation is one of the most important architectural decisions in BetavanX.

Traditional construction software often collapses these concepts into:

* rigid schedules
* monolithic gantt systems
* tightly coupled workflows

BetavanX intentionally separates them into:

# independent operational layers

This enables:

* reactive execution
* operational flexibility
* graph evolution
* dynamic resequencing
* location-aware adaptation

WITHOUT breaking system consistency.

---

# Most Important Architectural Achievement

The model correctly defines:

# Execution Logic ≠ Schedule

This is foundational.

Execution logic defines:

* operational possibilities
* sequencing behaviors
* dependency relationships
* workflow patterns
* execution constraints

Schedule defines:

# current operational arrangement

The schedule is only:

# temporary visualization of operational graph state

This distinction prevents the architecture from collapsing into rigid scheduling systems.

---

# Strong Architectural Concepts

# 1. Workflow Separation

The distinction between:

* workflow
* dependency
* constraint
* schedule

is extremely important.

This separation prevents future architectural coupling.

---

## Workflow

Defines:

# possible execution paths

---

## Dependency

Defines:

# operational execution relationships

---

## Constraint

Defines:

# operational limitations and blockers

---

## Schedule

Defines:

# current execution arrangement

---

# 2. Location-Aware Execution

The model correctly recognizes:

# construction execution is location-driven

Execution sequencing changes depending on:

* tower
* floor
* zone
* access conditions
* crew availability
* logistics constraints

The same workflow template may produce different execution realities.

This correctly reflects real construction behavior.

---

# 3. Repeatable Operational Cycles

The superstructure model correctly identifies:

# Repeatable Operational Construction Cycle

This is one of the most important construction execution behaviors.

Especially for:

* towers
* residential buildings
* hospitals
* hotels
* repetitive structures

This later evolves into:

* construction flowline logic
* location-based scheduling
* takt planning
* production flow optimization

---

# 4. Operational Parallelism

The architecture correctly avoids:

# false linear scheduling assumptions

Example:

Floor 15 → Structure
Floor 13 → Masonry
Floor 11 → MEP
Floor 9 → Finishes

This reflects:

# real construction operational flow

NOT simplified CPM-style sequencing.

---

# 5. Dynamic Resequencing

The architecture correctly assumes:

# execution order continuously evolves

based on:

* field conditions
* resource shortages
* delayed materials
* weather interruptions
* failed inspections
* operational priorities

This is a major architectural strength.

---

# Architectural Layers — Current Integration Status

The execution logic model successfully defines execution possibilities.
Several behavioral layers exist at different integration levels.

This section distinguishes:

* **Implemented** — exists in runtime MVP
* **Not yet integrated into Operational Graph** — exists but work-order-centric
* **Future** — not formally modeled

---

# Layer 1 — State Engine

**Previous review finding:** Missing State Engine

**Updated finding:** Lifecycle Engine **exists** — not yet integrated into Operational Graph

**Status:** Partial

### Current Reality

`backend/lifecycle/` implements:

* `TaskLifecycle`
* `WorkOrderLifecycle`
* `LifecycleTransition`
* `OperationalBlocker`

These operate on **Daily Work Orders** and task-centric flows in runtime MVP.

### Integration Gap

Lifecycle state is **not yet connected** to:

* `ActivityInstance`
* Workflow Graph nodes
* Graph-level state propagation

### Future Requirement (Operational Graph)

When integrated, the state engine should support:

* state transition rules on activity instances
* transition triggers from progress and constraints
* automatic state propagation across dependencies
* rollback and blocked state handling

Without graph integration, the operational graph remains behaviorally incomplete
at the Activity Instance level — even though work-order lifecycle exists today.

---

# Layer 2 — Constraint Resolution Logic

**Status:** Future (with interim runtime behavior)

Current constraints are primarily descriptive in execution logic docs.

Lifecycle **Operational Blockers** provide interim blocking behavior on work orders.

Dedicated graph-level **Constraint** entity resolution is an open question.
See `open-architecture-questions.md`.

Future constraint architecture may include:

* hard constraints
* soft constraints
* temporary constraints
* override logic
* escalation behavior
* dependency propagation

---

# Layer 3 — Event Engine

**Status:** Future

Operational events are referenced, but not formally modeled yet.

Future architecture may require operational event architecture for:

* manpower shortage
* equipment failure
* failed inspection
* weather interruption
* delayed delivery
* permit expiration

---

# Layer 4 — Resource Capacity Logic

**Status:** Future

The architecture references resources, but not yet capacity-aware execution behavior
at the Operational Graph level.

Workforce extension provides rich resource modeling when enabled — separately from
`core_operational.Resource` and not graph-integrated.

---

# Layer 5 — Progress Intelligence

**Status:** Partial

Progress exists through Daily Reports and KPI aggregation in runtime MVP.

Formal progress intelligence on **ActivityInstance** via **ProgressLog** is
schema foundation only — not production graph behavior.

---

# Layer 6 — Graph Mutation Logic

**Status:** Future

The operational graph is dynamic, but mutation rules are not yet formally defined.

Future architecture may require:

* node creation
* node splitting
* node merging
* resequencing
* dependency mutation
* workflow branching
* rollback behavior

This becomes **Operational Graph Evolution Logic**.

---

# Layer 7 — Recommendation Engine

**Previous review finding:** Missing Recommendation Engine

**Updated finding:** Recommendation Engine **exists** — not yet integrated into Operational Graph

**Status:** Partial

### Current Reality

`backend/services/recommendations/` generates operational recommendations.
Used by dashboard and task-detail services on work-order-centric data.

### Integration Gap

Recommendations are **not yet driven by**:

* Activity Instance graph state
* Workflow path context
* Location-based execution patterns
* Graph-level constraint propagation

Recommendations today enhance monitoring and visibility on the Runtime MVP stack.
Graph-native decision assistance remains target architecture.

---

# Critical Architectural Insight

BetavanX target direction is a **Stateful Operational Graph System** — not merely
project management, scheduling-only, or ERP software.

Current runtime is an **Operational Construction Visibility Platform** on
Daily Work Orders and Daily Reports, with several engines already active.

---

# Most Important Future Architectural Risk

The biggest architectural danger is:

# over-hardcoding workflows

Construction execution must remain:

* reactive
* adaptable
* operator-controlled
* field-driven

The system must support operational flexibility WITHOUT losing graph consistency,
execution visibility, operational integrity, or controllable execution state.

---

# Human-Controlled Operational Philosophy

BetavanX must always remain **operator-assisted**, not autonomous construction execution.

The platform supports visibility, coordination, forecasting, monitoring, and recommendations.
Final execution decisions remain human-controlled.

---

# Long-Term Architectural Direction

BetavanX architecture converges toward:

WBS
+
Workflow Graph
+
Location Graph
+
Dependency Logic
+
Constraint Engine
+
State Engine (graph-integrated)
+
Event Engine
+
Resource Logic
+
Operational Intelligence

This creates a **Dynamic Stateful Construction Operational Graph** evolving through
field execution, operational events, constraints, resource conditions, workflow decisions,
and execution reality.

---

# Final Architectural Identity

BetavanX target identity:

**Operational Construction Visibility Platform** with a **Stateful Operational Graph**
execution model — not static gantt scheduling, rigid ERP workflows, or bureaucratic
execution management.

See `current-vs-target-architecture.md` for the three-layer breakdown:
Runtime MVP · Operational Foundation · Target Graph.
