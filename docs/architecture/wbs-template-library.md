# BetavanX WBS Template Library

**Status:** Implemented (canonical WBS taxonomy)

**Scope:** Construction deliverables only.

Platform capabilities (analytics, dashboards, forecasting, workflow automation)
belong in `operational-capability-model.md` — not in this WBS catalog.

See also: `glossary.md`, `current-vs-target-architecture.md`

---

## Purpose

This library defines the BetavanX WBS Template structure as a
**Construction Operational Taxonomy**.

It is not a fixed schedule.

It is not a mandatory project sequence.

It is a reusable catalog of construction activity types that can later
be instantiated by:

- project
- location
- workflow context
- execution strategy

This means a template such as `Concrete Column` may appear many times
in many places without being tied to one universal schedule order.

---

## Library Rules

Each WBS Template in this library should be interpreted as:

- a reusable activity type
- a construction knowledge object
- an input to workflow and activity instantiation

It should not be interpreted as:

- a guaranteed predecessor-successor chain
- a single baseline schedule row
- a fixed project execution order

The actual executable work is created later as an Activity Instance:

`WBS Template + Location + Workflow Context = Activity Instance`

---

## Phase 0 — Pre-Construction

- Feasibility Study
- Geotechnical Study
- Architectural Design
- Structural Design
- BIM Coordination
- Clash Detection
- Quantity Surveying
- Permits

## Phase 1 — Site Setup

- Site Fencing
- Temporary Power
- Temporary Water
- Site Office
- Internet
- Site Access

## Phase 2 — Excavation & Shoring

- Excavation
- Soil Removal
- Level Control
- Nailing
- Shotcrete
- Drainage

## Phase 3 — Foundation

- Subgrade Preparation
- Lean Concrete
- Reinforcement
- Formwork
- Concrete Pour
- Concrete Testing

## Phase 4 — Structural Frame

- Columns
- Beams
- Slabs
- Curing
- Form Removal

## Phase 5 — Masonry & Partition

- Block Work
- Wall Posts
- Openings
- Lintels

## Phase 6 — MEP Rough-In

- Water Piping
- Drainage
- Electrical Conduits
- Cable Trays
- Fire Alarm
- CCTV

## Phase 7 — Finishes

- Plaster
- Flooring
- Painting
- Ceiling Systems

## Phase 8 — Facade

- Substructure
- Stone
- Curtain Wall
- Waterproofing

## Phase 9 — MEP Final Fix

- Equipment Installation
- Panels
- Lighting
- BMS

## Phase 10 — Vertical Transportation

- Elevator Rails
- Motors
- Cabins
- Testing

## Phase 11 — External Works

- Pavement
- Landscaping
- Asphalt
- Lighting

## Phase 12 — Testing & Commissioning

- Electrical Testing
- HVAC Testing
- Startup
- Integration Tests

## Phase 13 — Handover

- Punch List
- As-Built Documents
- O&M Manuals
- Final Delivery

## Phase 14 — HSE

- PPE
- Work Permits
- Height Safety
- Waste Management

## Phase 15 — Quality Control

- Material Testing
- Execution Inspection
- NCR
- Laboratory Reports

---

## WBS Boundary — Platform Capabilities Excluded

The following are **operational capabilities**, not construction deliverables.
They were removed from this WBS catalog during documentation reconciliation.

Relocated to `operational-capability-model.md` (Section 08):

- Data Governance
- KPI Dashboards
- Workflow Automation
- Operational Analytics
- Forecasting

Do not add platform intelligence behaviors to WBS phases.

---

## How the Library Should Be Used

The library is intended to support four core behaviors:

### 1. Template Selection

Projects choose the relevant templates from the library depending on:

- project type
- delivery strategy
- technical scope
- reporting needs

### 2. Location-Based Instantiation

Templates are instantiated per location.

Examples:

- Columns @ Tower A / Floor 2
- Block Work @ Tower B / Floor 5 / Zone East
- Lighting @ External Works / Parking Area

### 3. Workflow Mapping

Templates can be connected to workflow nodes and possible execution
paths without forcing one rigid master sequence.

Example:

- Slabs may lead to Masonry, MEP Rough-In, or Waterproofing depending
  on execution strategy and location readiness.

### 4. Schedule Generation

Schedules are later generated from activity instances and dependencies,
not directly from the library ordering shown above.

The phase order in this document is an operational grouping structure,
not a universal project sequence.

---

## Classification Guidance

This library should remain understandable by engineers and planners.

Each template should eventually be able to carry lightweight metadata
such as:

- phase
- discipline
- typical unit of measure
- default resource categories
- quality checkpoints
- safety relevance
- location applicability

This metadata should support instantiation and visibility, not create
administrative overhead.

---

## Important Boundary

The presence of a WBS Template in this library does not mean:

- it must exist in every project
- it must start after one specific prior template
- it must appear only once
- it owns schedule logic

The WBS Library is construction taxonomy.

Workflow Graph plus Location plus Operational Reality determine how
those templates become executable work.

---

## Summary

This WBS Template Library gives BetavanX a reusable construction-native
knowledge base.

It supports future planning and activity instantiation
without forcing the platform into a simplistic:

`WBS -> static schedule`

model.

The correct interpretation is:

`WBS Templates -> reusable activity types`

which are later transformed into:

`Activity Instances -> real executable operational work`
