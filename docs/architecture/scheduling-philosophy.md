# BetavanX Scheduling Philosophy

## Purpose

This document defines how scheduling should be understood in BetavanX.

Scheduling is not the core model.

Scheduling is the **dynamic operational visualization** of the core
operational graph.

That means BetavanX should not be designed as a static planning
application with reporting attached later.

Instead, planning and scheduling should emerge from execution-aware
operational entities.

---

## Core Principle

The Gantt chart is only a visualization layer.

The real system underneath is:

- WBS Templates
- Location System
- Workflow Graph
- Activity Instances
- Dependencies
- Resource Assignments
- Progress Reality

The schedule exists to make this operational graph visible in time.

It should not become the single source of truth for the entire
platform.

---

## What Scheduling Represents

In BetavanX, a schedule should represent:

- selected executable activities
- their temporal placement
- their dependency relationships
- their current progress state
- their operational constraints
- their assigned resources

A schedule is therefore a dynamic arrangement of operational entities,
not a fixed spreadsheet of tasks.

---

## What Scheduling Is Not

Scheduling is not:

- a static baseline file with no feedback loop
- a hardcoded project sequence engine
- a replacement for WBS
- a replacement for workflow logic
- a replacement for execution reality

It should also not force BetavanX into a heavy CPM or ERP-first product
identity.

The platform should remain:

- lightweight
- visual
- operational
- field-oriented

---

## Inputs to Scheduling

Schedules are generated from the operational graph and its current
state.

Primary inputs:

- workflow graph
- activity instances
- dependency relationships
- location hierarchy
- resource assignments
- operational constraints
- progress logs
- execution status

This keeps scheduling tied to real site information rather than only to
original plan assumptions.

---

## Reactive Scheduling

Construction scheduling is not static.

It must react to:

- delays
- blocked work fronts
- manpower shortages
- material shortages
- equipment failures
- changed execution strategy
- early completions
- location readiness changes

This does not require advanced optimization engines in the core.

It simply requires that the architecture allows schedule views and
dates to be recalculated or adjusted when operational reality changes.

---

## Planner Interaction Model

The project manager or site planner should be able to:

- choose next valid activities
- arrange multiple execution paths
- drag and place activities visually
- create or edit dependencies
- assign resources immediately
- resequence work when site conditions change
- compare alternative execution strategies

This is why the workflow graph must allow multiple valid successors
instead of one hardcoded chain.

The planner is not just filling dates.

The planner is selecting and organizing executable operational paths.

---

## Relationship to WBS

WBS Templates define construction taxonomy.

They provide reusable construction knowledge such as:

- Columns
- Beams
- Masonry
- Waterproofing
- MEP Rough-In

The schedule should be generated from Activity Instances created from
those templates, not directly from the WBS list itself.

This matters because:

- the same WBS Template may appear in many locations
- not every template is active at the same time
- execution order may vary by project and location

Therefore:

**WBS is not the schedule.**

---

## Relationship to Location

The schedule must support location-aware planning.

Examples:

- Tower A and Tower B may progress differently
- Floor 5 may be blocked while Floor 3 continues
- one zone may be ahead while another remains delayed

The schedule should be able to visualize and reorganize activities by:

- tower
- floor
- zone
- area
- execution package

This is essential for real construction management.

---

## Relationship to Dependencies

Dependencies are lightweight operational coordination relationships.

The architecture should support:

- FS
- SS
- FF
- lag values

These are enough for the foundation.

The goal is to support realistic coordination without overbuilding the
core into a complex scheduling engine too early.

---

## Relationship to Progress Reality

Progress logs and actual execution data must influence the schedule.

Examples:

- delayed concrete pour shifts related finishing activities
- low manpower progress reduces confidence in near-term completion
- blocked location prevents downstream work in that area
- completed work unlocks next candidate activities

This is how BetavanX supports:

- monitor
- control
- replan

instead of stopping at initial planning.

---

## Minimum Scheduling Capabilities

The foundational architecture should support:

- dynamic activity placement
- drag-and-drop planning
- dependency creation
- dependency editing
- schedule grouping by location
- reactive schedule updates
- parallel path planning
- operational rescheduling

This is enough to establish the right architecture without building a
full optimization suite.

---

## Future Direction

If the foundation is correct, future evolution can support:

- delay analysis
- forecasting
- productivity-aware planning
- resource balancing
- 4D BIM views
- AI-assisted planning

without redesigning the core scheduling philosophy.

The scheduling layer should stay a consumer of the operational graph,
not the owner of all construction logic.

---

## Summary

BetavanX scheduling should be understood as:

**dynamic operational visualization of the executable construction
graph**

The core system owns construction knowledge, workflow logic, location,
dependencies, and execution reality.

The schedule turns those into a usable time-based coordination view for
engineers and planners.

---

# Scheduling Calculation Philosophy

BetavanX scheduling calculations may combine:

- graph traversal logic
- CPM-based calculations
- lightweight heuristic adjustments

depending on operational context.

The scheduling engine is designed to remain:

- reactive
- operational
- lightweight
- graph-aware

NOT rigid enterprise scheduling bureaucracy.

Advanced forecasting and optimization systems
may evolve in future platform phases,
but are intentionally not part of the current operational core.
