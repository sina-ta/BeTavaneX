# BetavanX Workflow Graph

## Purpose

This document defines the workflow philosophy underneath BetavanX.

The workflow graph is the real operational coordination layer of the
platform.

It is not the same thing as:

- WBS hierarchy
- a static schedule
- a fixed project baseline

The workflow graph answers:

**What execution paths are possible right now?**

---

## Core Philosophy

Real construction workflows are not single-path sequences.

They:

- branch
- overlap
- repeat
- depend on location
- react to constraints
- change with execution strategy

Because of that, the workflow engine must support:

`Activity A -> B / C / D`

not only:

`Activity A -> B`

The graph defines **operational possibilities**, not compulsory project
order.

---

## Why WBS Is Not the Workflow

The WBS library is construction taxonomy.

It tells the platform what kinds of work exist:

- Excavation
- Reinforcement
- Formwork
- Masonry
- Waterproofing

It does not tell the platform the one true execution route for every
project.

The workflow graph exists because two projects may use the same WBS
Templates but sequence and coordinate them differently depending on:

- site conditions
- location readiness
- strategy
- weather
- access
- resources
- design constraints

---

## Workflow Graph Components

### Workflow Nodes

Workflow nodes represent meaningful operational steps.

Examples:

- Excavation
- Lean Concrete
- Reinforcement
- Formwork
- Concrete Pour
- Columns
- Underground Utilities
- MEP Rough-In
- Waterproofing

Nodes should be reusable across many projects and locations.

They express workflow meaning, not schedule placement.

---

### Workflow Edges

Workflow edges define valid transitions or continuations between nodes.

Examples:

- Excavation -> Lean Concrete
- Excavation -> Dewatering
- Lean Concrete -> Reinforcement
- Slab Concrete -> Masonry
- Slab Concrete -> MEP Rough-In

An edge should be interpreted as:

> this next step is operationally valid or commonly expected

not:

> this next step is mandatory in every situation

---

## Suggested Path, Not Forced Path

BetavanX should treat workflow edges as:

- suggestions
- operational possibilities
- planning guidance
- visibility logic

The graph should not hard-lock the project into one fixed sequence.

This is especially important because construction teams often make
tactical choices such as:

- starting work in another zone first
- running parallel crews
- skipping ahead in one area while another area is blocked
- splitting a sequence across floors
- delaying one branch while another continues

The platform must support those realities.

---

## Example Workflow Branches

### Earthworks and Foundation

Excavation can lead to:

- Lean Concrete
- Dewatering
- Utilities

Foundation can lead to:

- Columns
- Retaining Wall
- Underground Utilities

### Structural and Envelope

Columns can lead to:

- Beams
- Slabs
- Form Removal Preparation

Slab Concrete can lead to:

- Masonry
- MEP Rough-In
- Waterproofing

### Interior Works

Masonry can lead to:

- Plaster
- Opening Preparation
- MEP Follow-Up

MEP Rough-In can lead to:

- Testing
- Ceiling Systems
- Final Fix

These are not universal hard rules.

They are operationally reasonable next-step options.

---

## Relationship to Location

Workflow paths should be interpreted together with location.

Example:

- Slab Concrete @ Floor 2 may unlock Masonry @ Floor 2
- Slab Concrete @ Floor 2 does not automatically unlock Masonry @ Floor 8

That means the graph is reusable, but execution happens through
location-aware activity instances.

In practice:

- the workflow graph defines possible logic
- the location system scopes where that logic applies
- activity instances turn both into real executable work

---

## Relationship to Dependencies

Workflow edges are not identical to dependencies.

Difference:

- **Workflow edge** = operationally valid next path
- **Dependency** = explicit relationship between two activity instances

Example:

- the workflow graph may allow `Slab -> Masonry`
- a planner may then create a dependency:
  `Slab Concrete @ Floor 2 -> Masonry @ Floor 2`

This distinction keeps the architecture flexible:

- graph defines what is possible
- dependencies define what is currently chosen

---

## Relationship to Scheduling

The schedule is only one view of the workflow graph.

The graph should exist before and underneath the Gantt chart.

The Gantt chart visualizes:

- selected activity instances
- their current dates
- their chosen dependencies
- their progress state

It does not define the graph itself.

This separation is critical because schedule layouts may change while
the underlying operational logic stays valid.

---

## Lightweight Design Rules

To keep the workflow engine construction-native and understandable, the
core workflow graph should remain lightweight.

It should support:

- node definitions
- edge definitions
- multiple possible successors
- optional edge metadata
- location-aware instantiation
- planner-selected paths

It should not yet require:

- complex optimization logic
- heavy BPM/workflow orchestration
- enterprise approval bureaucracy
- giant rule engines

The graph is a coordination model, not a workflow automation monster.

---

## Operational Use in BetavanX

The workflow graph should help the platform answer practical questions:

- what can be started next
- what is blocked
- what can run in parallel
- what paths are valid in this location
- what changed because of delays or constraints

That is how BetavanX supports:

- dynamic planning
- reactive scheduling
- execution visibility
- workflow coordination

without pretending construction is linear.

---

## Summary

BetavanX should model workflow as a reusable graph of possible
construction paths.

The most important architectural rule is:

**workflow defines possibilities, not rigid commands**

This keeps the platform aligned with real construction execution where
branching, overlap, repetition, and tactical replanning are normal.