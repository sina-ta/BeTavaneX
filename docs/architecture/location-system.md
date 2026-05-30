# BetavanX Location System

**Status:** Future (target architecture) — schema foundation exists

See: `current-vs-target-architecture.md`, `glossary.md`

---

## Purpose

Construction execution is fundamentally location-based.

BetavanX must treat location as a first-class operational structure,
not as a label attached late to schedule rows.

This document defines the location-aware execution model that sits
under planning, progress, scheduling, and operational monitoring.

---

## Core Principle

Activities are not just defined by *what* they are.

They are also defined by *where* they happen.

Examples:

- Concrete Column @ Tower A / Floor 2
- Brick Wall @ Zone East
- MEP Rough-In @ Basement Level
- Waterproofing @ Roof Sector B

This means location is a core part of activity instantiation, progress
tracking, and scheduling.

---

## Location Tree

The location system should be hierarchical.

Typical structure:

```text
Project
├── Tower A
│   ├── Basement
│   ├── Floor 1
│   ├── Floor 2
│   │   ├── Zone East
│   │   ├── Zone West
│   │   └── Room 201
│   └── Roof
└── External Works
    ├── Landscape Zone
    ├── Pavement Area
    └── Lighting Corridor
```

The exact hierarchy may vary by project, but the model must support:

- towers
- floors
- zones
- rooms
- sectors
- areas

The goal is flexibility without losing clarity.

---

## Location Node Types

The platform should allow different location node categories such as:

- project
- building/tower
- block
- basement
- floor/level
- zone
- room
- sector
- external area

These categories help users understand where work is being tracked, but
the model should remain flexible enough for different project types.

---

## Hierarchical Behavior

The Location Tree must support parent-child relationships.

This enables:

- roll-up progress by parent location
- roll-up delays by parent area
- grouped schedule views
- filtered activity visibility
- repeatable planning patterns

Example:

- progress at `Zone East` contributes to `Floor 2`
- progress at `Floor 2` contributes to `Tower A`
- progress at `Tower A` contributes to the overall project

This allows both detailed and executive-level visibility from the same
operational data.

---

## Repeatable Cycles

Construction frequently repeats similar work across multiple locations.

Examples:

- one slab cycle per floor
- one masonry cycle per apartment unit
- one MEP rough-in cycle per room or zone

The location model must support repeatable execution patterns without
copying business logic into each schedule row.

That means BetavanX should be able to instantiate the same WBS Template
or workflow path across many sibling locations.

Examples:

- Column Reinforcement @ Floor 1
- Column Reinforcement @ Floor 2
- Column Reinforcement @ Floor 3

The template stays the same.

The executable activity changes because the location changes.

---

## Location-Aware Activity Instantiation

The location system directly participates in creating Activity
Instances.

Formula:

`WBS Template + Location + Workflow Context = Activity Instance`

Examples:

- Concrete Column @ Tower A / Floor 2 / Zone East
- Electrical Conduits @ Tower B / Floor 5 / Corridor
- Asphalt @ External Works / Area South

This is essential because planning and progress are rarely meaningful
without location.

---

## Location and Workflow

Workflow logic must interact with location, not ignore it.

Example:

- Slab Concrete @ Floor 3 may unlock Masonry @ Floor 3
- it does not automatically unlock all masonry in the entire project

This means workflow edges are reusable, but their real operational
impact is resolved at the location level.

The system should be able to answer:

- what can start in this floor
- what is blocked in this zone
- which area is lagging
- which tower is ahead

---

## Location-Based Progress Tracking

Progress should be trackable per location.

Examples:

- structural frame progress by tower
- masonry progress by floor
- rough-in progress by zone
- finishing progress by room cluster

Location-based tracking enables:

- more accurate operational visibility
- easier site coordination
- more realistic reporting
- location-based delay analysis
- location-based schedule views

This is far more useful than only tracking progress by activity type.

---

## Location-Based Scheduling

Scheduling in BetavanX must be location-aware.

The system should allow users to:

- group schedule views by tower, floor, or zone
- compare progress between locations
- stagger work by location
- delay or resequence specific areas
- run parallel strategies in different locations

This is one of the reasons BetavanX should not collapse WBS and
schedule into one model.

The location tree gives execution geography.

The schedule visualizes time.

They must cooperate, not merge into one concept.

---

## Location and Constraints

Location is also where many operational constraints appear.

Examples:

- one floor not ready
- one zone blocked by access issues
- one room waiting for inspection
- one tower delayed by equipment movement

The location system should therefore support association with:

- readiness states
- blockages
- inspections
- handover states
- location-specific notes

This makes location not just a map, but an operational control surface.

---

## Design Rules

To keep the model lightweight and construction-native:

- locations should be hierarchical
- location categories should be flexible
- activity instances should always be location-aware
- schedule views should be able to group by location
- progress should roll up through the location tree

The system should avoid:

- overcomplicated BIM-only abstractions in the core
- forcing a rigid universal location schema on all projects
- treating locations as cosmetic tags

---

## Summary

The Location System defines **where execution happens**.

It is one of the core pillars of the BetavanX operational graph:

- WBS defines what kind of work exists
- Workflow defines possible paths
- Location defines where work occurs
- Activity Instances turn all three into executable reality

Without a strong location model, construction execution cannot be
represented accurately.

