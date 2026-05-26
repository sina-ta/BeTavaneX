# BetavanX Core Operational Model

## Purpose

This document defines the foundational operational data model of
BetavanX as an **Operational Construction Visibility Platform**.

The objective is not to build a simple Gantt application.

The objective is to establish a lightweight core architecture that can
support:

- execution visibility
- operational monitoring
- dynamic planning
- reactive scheduling
- workflow coordination
- future operational intelligence

without forcing heavy ERP abstractions or static schedule logic into
the center of the system.

---

## Core Principle

**WBS is not the schedule.**

BetavanX must keep the following concerns separate:

- construction knowledge
- workflow logic
- location hierarchy
- execution reality
- schedule visualization

The platform should not model the project as:

`WBS -> fixed sequence -> static Gantt`

The platform should model the project as:

`WBS Templates + Location System + Workflow Graph + Operational Reality`

which produces a **Dynamic Executable Operational Graph**.

---

## Operating Loop

The core operational loop of BetavanX is:

`Plan -> Execute -> Monitor -> Control -> Replan`

This loop is continuous, not one-time.

The model must support operational change caused by:

- delays
- resource shortages
- equipment failures
- blocked locations
- progress updates
- field constraints
- execution strategy changes

That means the core system must preserve both:

1. what *can* happen
2. what *is actually happening*

---

## Core Entities

### Project

The project is the top-level operational container.

It owns:

- project identity
- project scope
- location tree
- selected WBS templates
- workflow graph configuration
- activity instances
- operational logs

The project does **not** define a single hardcoded execution path.

Its purpose is to host the operational graph for a real construction
environment.

---

### WBS Template

The WBS Template defines a **construction activity type**, not an
execution instance and not a schedule row.

Examples:

- Concrete Column
- Beam Reinforcement
- Brick Wall
- Excavation
- Curtain Wall Installation

The WBS Template is construction knowledge taxonomy.

It should describe:

- phase
- trade or discipline
- work type
- typical inputs
- typical outputs
- default resource categories
- reusable operational metadata

It should **not** directly define:

- exact start date
- exact finish date
- fixed predecessor list for every project
- one universal project sequence

---

### Location Tree

The Location Tree defines **where** execution happens.

Typical hierarchy:

`Project -> Tower -> Floor -> Zone -> Room/Sector/Area`

The location system is a first-class operational structure because
construction execution is fundamentally location-based.

The Location Tree enables:

- activity instantiation by place
- location-specific progress tracking
- location-specific constraints
- repeatable work cycles
- schedule grouping by execution area

---

### Workflow Node

A Workflow Node defines an operational activity state or step within
the graph.

In practical terms, a workflow node represents a meaningful unit of
construction workflow logic, such as:

- Excavation
- Lean Concrete
- Reinforcement
- Concrete Pour
- MEP Rough-In
- Waterproofing

The node defines operational meaning, not a specific date on a chart.

It can be linked to one or more WBS Templates and reused across
locations and project areas.

---

### Workflow Edge

A Workflow Edge defines a **possible execution path** between workflow
nodes.

Examples:

- Foundation -> Columns
- Foundation -> Underground Utilities
- Slab Concrete -> Masonry
- Slab Concrete -> MEP Rough-In

The key idea is that workflow edges define **valid operational
possibilities**, not mandatory one-path project logic.

An edge may represent:

- a common sequence
- a preferred continuation
- a parallel opportunity
- a conditional path

This keeps the system flexible enough for real site conditions.

---

### Activity Instance

The Activity Instance is the most important executable entity in the
model.

It is created from:

`WBS Template + Location + Workflow Context = Activity Instance`

Examples:

- Concrete Column @ Tower A / Floor 2 / Zone East
- Brick Wall @ Basement / Room B-14
- Cable Tray Installation @ Tower B / Floor 6

An Activity Instance is the real operational object that teams plan,
assign, monitor, delay, complete, and re-sequence.

It should hold lightweight runtime data such as:

- project reference
- WBS template reference
- location reference
- workflow node reference
- execution status
- dependency links
- assigned resources
- planned dates
- actual dates
- progress values
- constraint flags

The Activity Instance is where construction taxonomy becomes execution
reality.

---

### Dependencies

Dependencies represent relationships between activity instances.

The architecture must support lightweight dependency types:

- Finish-to-Start (FS)
- Start-to-Start (SS)
- Finish-to-Finish (FF)
- optional lag values

Dependencies should be lightweight and operational.

They are used to coordinate execution and visualization, not to force a
heavy CPM engine into the platform.

Dependencies may come from:

- workflow suggestions
- planner decisions
- field-created constraints
- temporary tactical sequencing

---

### Resources

BetavanX core should support only lightweight operational resource
categories:

- manpower
- materials
- equipment

The core is not an HR or ERP system.

Resources in the core model exist to answer operational questions such
as:

- what is assigned
- what is missing
- what is blocked
- what affects execution readiness

Advanced workforce intelligence can exist as an extension, but core
execution must not depend on it.

---

### Assignments

Assignments connect resources to activity instances.

Examples:

- 6 workers assigned to slab reinforcement
- one formwork team assigned to column activity
- concrete pump allocated to a pour activity
- gypsum material reserved for a finishing activity

Assignments should remain lightweight and execution-oriented.

Their purpose is immediate planning and visibility, not enterprise
resource bureaucracy.

---

### Progress Logs

Progress Logs are the operational truth layer.

They capture what actually happened in the field.

Typical information includes:

- reported quantity
- manpower count
- equipment hours
- delays
- status
- weather
- approval state
- timestamp
- reporter

Progress logs are the foundation for:

- monitoring
- validation
- KPI calculation
- delay analysis
- future forecasting
- future optimization

The system should treat Progress Logs as the most reliable source of
execution reality.

---

## Entity Relationships

At a conceptual level:

- a **Project** owns many **Locations**
- a **Project** uses many **WBS Templates**
- a **Workflow Graph** defines valid relationships between workflow
  nodes
- a **Location Tree** defines execution geography
- an **Activity Instance** is created from WBS + Location + Workflow
  Context
- an **Activity Instance** may have many **Dependencies**
- an **Activity Instance** may have many **Assignments**
- an **Activity Instance** may accumulate many **Progress Logs**

This separation matters because:

- WBS answers **what kind of work**
- Location answers **where**
- Workflow answers **what can come next**
- Activity Instance answers **what is executable now**
- Schedule answers **how it is visualized in time**

---

## What the Core Model Is Not

The core model should not become:

- a static WBS-to-Gantt converter
- a full ERP resource system
- a heavy workflow bureaucracy engine
- a full optimization engine
- an AI planning system

Those capabilities may evolve later, but the core data model must stay:

- lightweight
- visual
- operational
- construction-native
- field-oriented
- understandable by real engineers

---

## Future-Safe Direction

This model is intentionally small but future-capable.

It should support later evolution toward:

- reactive scheduling
- delay propagation analysis
- productivity analytics
- resource balancing
- 4D BIM coordination
- AI-assisted planning
- digital construction intelligence

without redesigning the core entities.

The foundation should remain:

**simple enough for daily execution**

while being

**structured enough for future intelligence**.