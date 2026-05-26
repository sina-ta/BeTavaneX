# BetavanX — Operational Behavior Model

# Core Principle

BetavanX is NOT a static project scheduling system.

It is:

# A Reactive Operational Construction System

The platform continuously reacts to:

* execution reality
* operational constraints
* resource changes
* progress deviations
* field conditions

through an operational feedback loop.

---

# Core Operational Loop

Plan
→ Execute
→ Monitor
→ Analyze
→ Control
→ Replan

This loop is continuous throughout the project lifecycle.

The schedule is never considered permanently fixed.

---

# Operational Behavior Layers

The system behavior is divided into:

1. Knowledge Layer
2. Workflow Layer
3. Execution Layer
4. Monitoring Layer
5. Control Layer
6. Visualization Layer

---

# 1. Knowledge Layer Behavior

## Purpose

Defines WHAT can exist in construction.

This layer contains:

* WBS Templates
* Activity Taxonomy
* Construction Categories
* Standard Construction Knowledge

---

## Rules

WBS templates are:

* reusable
* non-scheduled
* location-independent
* operationally descriptive

WBS does NOT define execution order.

Example:

Concrete Column
is:
a construction activity type

NOT:
a scheduled activity instance.

---

# 2. Workflow Layer Behavior

## Purpose

Defines POSSIBLE operational execution paths.

The workflow layer is:

# graph-based

NOT linear.

---

## Workflow Rules

Activities may:

* branch
* merge
* overlap
* repeat
* execute in parallel
* depend on constraints
* react to operational conditions

---

## Valid Next Activities

Each workflow node may lead to:

* one activity
* multiple activities
* optional activities
* conditional activities

Example:

Foundation
→ Columns
→ Underground Utilities
→ Retaining Wall

The system suggests:
possible next activities

The user decides:
actual execution sequence.

---

## Workflow Philosophy

The system assists planning.

It does NOT force planning.

BetavanX acts as:

# Operational Planning Assistant

NOT autonomous scheduler.

---

# 3. Location System Behavior

## Purpose

Defines WHERE execution occurs.

Construction activities are always location-aware.

---

## Location Rules

Locations support:

* hierarchical structures
* repeatable cycles
* parallel execution
* independent progress tracking

Example:

Tower A
└── Floor 2
└── Zone East

---

## Activity Instantiation

Real executable activities are generated using:

WBS Template
+
Location
+
Workflow Context
================

Activity Instance

Example:

Concrete Column @ Floor 2

---

## Repeatable Cycle Rules

Certain workflows repeat across locations.

Examples:

* floor cycles
* room finishing cycles
* facade installation cycles

The system must support:

* template replication
* cycle-based execution
* location-specific progress

without duplicating logic manually.

---

# 4. Scheduling Behavior

## Purpose

Defines WHEN activities are planned.

Scheduling is:

# dynamic operational visualization

NOT fixed planning logic.

---

## Scheduling Rules

Schedules are generated from:

* workflow graph
* activity instances
* dependencies
* operational constraints
* resource assignments
* execution reality

---

## User Interactions

The project manager must be able to:

* drag activities on gantt
* shift execution sequences
* create dependencies
* arrange parallel paths
* modify workflows visually
* assign resources directly
* update execution strategy dynamically

---

## Dynamic Rescheduling

When operational conditions change:

* gantt updates
* dependencies react
* critical path recalculates
* forecasts update
* schedule shifts visually

Examples:

* delay detected
* manpower shortage
* equipment failure
* material delay
* weather issue

The schedule continuously adapts.

---

# 5. Dependency Behavior

Dependencies define operational relationships.

Supported lightweight dependency types:

* Finish-to-Start (FS)
* Start-to-Start (SS)
* Finish-to-Finish (FF)
* Lag relationships

---

## Dependency Philosophy

Dependencies are operational coordination tools.

NOT rigid bureaucratic controls.

The system must support:

* soft dependencies
* editable relationships
* dynamic sequencing

---

# 6. Resource Behavior

## Purpose

Defines operational resource allocation.

Resources are lightweight operational entities.

Supported resource categories:

* manpower
* materials
* equipment

---

## Resource Assignment Rules

Resources may be:

* suggested automatically
* assigned manually
* adjusted dynamically

Assignments support:

* planned quantities
* actual quantities
* allocation windows

---

## Resource Shortage Detection

The system must detect:

* insufficient manpower
* missing materials
* equipment conflicts
* allocation overlaps

and notify operational impact.

---

# 7. Progress Monitoring Behavior

## Purpose

Captures REAL execution data.

This is the operational truth layer.

---

## Progress Rules

Progress logs capture:

* actual progress
* actual manpower
* actual material usage
* delays
* issues
* field observations
* operational notes

---

## Planned vs Actual

The system continuously compares:

planned progress
vs
actual execution

Example:

Planned:
80%

Actual:
45%

---

## Operational Monitoring

The system detects:

* delays
* productivity drops
* resource shortages
* execution anomalies
* critical path risks

based on real operational data.

---

# 8. Control Behavior

## Purpose

Transforms monitoring into operational action.

---

## Control Rules

The system may:

* suggest alternate paths
* recommend resource shifts
* warn about delays
* identify critical risks
* highlight operational bottlenecks

The project manager remains the decision-maker.

---

# 9. Visualization Behavior

## Purpose

Expose operational reality visually.

---

## IMPORTANT PRINCIPLE

Gantt charts are NOT the operational system.

Gantt is ONLY:

# visualization of the operational graph

---

## Visualization Components

The operational graph may be visualized as:

* gantt charts
* progress boards
* dashboards
* timelines
* location maps
* operational analytics

All visualizations originate from the same operational graph.

---

# 10. Operational Intelligence Philosophy

BetavanX intelligence is:

# operationally derived

NOT manually fabricated.

Intelligence originates from:

* progress logs
* execution history
* operational events
* workflow behavior
* resource performance
* schedule deviations

---

# 11. Human-Centered Philosophy

BetavanX communicates using:

# simple construction operational language

NOT enterprise jargon.

The system should feel:

* practical
* visual
* operational
* construction-native
* lightweight
* field-oriented

Complex operational logic remains underneath the UX.

---

# 12. Architectural Constraints

The system must remain:

* modular
* graph-capable
* location-aware
* operationally reactive
* extension-friendly

WITHOUT becoming:

* ERP complexity
* enterprise bureaucracy
* rigid scheduling software
* over-automated AI system

---

# Final Architectural Identity

BetavanX is:

# A Graph-Based Operational Construction Visibility Platform

that continuously connects:

construction knowledge
+
workflow possibilities
+
location-aware execution
+
real operational data
+
dynamic scheduling
+
continuous monitoring

into a unified operational construction system.

---

# 13. Operational Decision Rules

BetavanX is not only a monitoring platform.

It is also:

# Operational Decision Support System

The platform continuously evaluates operational conditions
and provides lightweight execution recommendations.

Decision rules are operationally derived,
not manually bureaucratic workflows.

---

## Example Rules

### Critical Path Delay

IF:
critical path delay > 2 days

THEN:
suggest:
- increase manpower
- parallelize successor activities
- shift non-critical resources
- adjust execution sequence

---

### Productivity Drop

IF:
actual progress < planned progress by 20%

THEN:
flag:
- productivity risk
- schedule deviation

AND suggest:
- additional crew
- overtime
- workflow adjustment

---

### Resource Shortage

IF:
required manpower > available manpower

THEN:
suggest:
- reallocation
- delayed execution
- alternate sequencing

---

### Material Delay

IF:
critical material delivery delayed

THEN:
suggest:
- resequencing activities
- activating alternate workflow path
- shifting parallel tasks forward

---

# Decision Philosophy

BetavanX provides:

- operational guidance
- execution visibility
- reactive recommendations

The project manager remains the final decision-maker.

The system assists operational control,
NOT autonomous execution.

---

# 14. Operational Metrics Layer

BetavanX internally supports operational performance metrics
inspired by global project management standards.

These metrics exist primarily in:

- monitoring systems
- analytics layers
- forecasting layers
- operational intelligence systems

NOT as heavy enterprise UX terminology.

---

## Supported Metrics

Examples include:

- PV (Planned Value)
- EV (Earned Value)
- AC (Actual Cost)
- SPI (Schedule Performance Index)
- CPI (Cost Performance Index)
- EAC (Estimate At Completion)

---

# Metrics Philosophy

Operational metrics remain:

- lightweight
- contextual
- execution-oriented

The platform communicates using:

# simple construction operational language

while advanced metrics remain underneath the system logic.

---

# 15. Operational State Management

Construction execution is state-driven.

Each Activity Instance transitions through operational states.

---

## Activity States

Examples:

- planned
- ready
- assigned
- in_progress
- blocked
- delayed
- under_review
- completed
- validated
- archived

---

# State Philosophy

Operational states represent:

# real execution conditions

NOT bureaucratic administrative labels.

State transitions are driven by:

- execution progress
- operational events
- validations
- constraints
- approvals
- field conditions

---

# Concurrency Awareness

BetavanX is designed as a collaborative operational platform.

Multiple users may interact with the same operational entities.

Examples:

- project managers
- site engineers
- supervisors
- coordinators

The architecture must preserve:

- operational consistency
- data integrity
- reliable progress tracking

during concurrent operational updates.

---

# Atomic Operational Actions

Critical operational updates should behave atomically.

Examples:

- resource reassignment
- dependency changes
- progress updates
- schedule modifications

The system architecture must support:

- reliable state transitions
- operational consistency
- recoverable execution behavior

without introducing unnecessary enterprise complexity.

---

