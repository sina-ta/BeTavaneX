# DEPRECATED

**Status:** Deprecated

This document is **deprecated** and must not be used as a canonical WBS source.

---

## Canonical Source

Use instead:

**`docs/architecture/wbs-template-library.md`**

That document is the single authoritative BetavanX construction WBS taxonomy.

---

## Why Deprecated

This file duplicated `wbs-template-library.md` with:

- different numbering (Level 2 domains vs phases)
- incomplete coverage (stops mid–Mechanical Works)
- mixed terminology (`Operational Task Node` vs canonical `Activity Instance`)

BetavanX maintains **one** WBS definition to avoid competing taxonomies.

---

## Terminology Note

| Deprecated term | Canonical term |
|-----------------|----------------|
| Operational Task Node | Activity Instance (see `glossary.md`) |
| Operational Task | User-facing label only |

---

## Historical Reference

The content below is preserved for historical reference only.
Do not extend or maintain this structure.

---

# BetavanX — Construction WBS Template

# Core WBS Philosophy

This WBS is NOT:

* a static schedule
* a gantt structure
* a fixed execution sequence

This WBS is:

# Construction Operational Knowledge Structure

The WBS defines:

* construction knowledge
* operational deliverables
* executable work categories
* reusable construction templates

Execution emerges dynamically through:

WBS Template
+
Location
+
Workflow Context
================
Operational Task Node

---

# WBS Design Principles

This WBS is designed around:

* operational controllability
* measurable deliverables
* adaptive granularity
* recursive decomposition
* location-aware execution
* graph-compatible workflows

---

# Important Principle

This WBS intentionally avoids:

* fixed floor definitions
* hardcoded project-specific locations
* rigid scheduling assumptions

Locations such as:

* floors
* towers
* zones
* sectors
* rooms

must be injected dynamically during activity instantiation.

---

# LEVEL 1 — PROJECT

Project

---

# LEVEL 2 — CONSTRUCTION DOMAINS

01 Design & Engineering
02 Procurement & Logistics
03 Site Preparation
04 Earthworks
05 Substructure
06 Superstructure
07 Architectural Works
08 Mechanical Works
09 Electrical Works
10 Low Current Systems
11 Vertical Transportation
12 External Works
13 Testing & Commissioning
14 Handover & Closeout
15 Quality Management
16 Safety Management

---

# 01 — DESIGN & ENGINEERING

01.01 Architectural Design
01.02 Structural Design
01.03 Mechanical Design
01.04 Electrical Design
01.05 Low Current Design
01.06 BIM Coordination
01.07 Clash Detection
01.08 Shop Drawings

---

# 02 — PROCUREMENT & LOGISTICS

02.01 Material Procurement
02.02 Equipment Procurement
02.03 Vendor Management
02.04 Logistics Coordination
02.05 Delivery Tracking
02.06 Procurement Inspection

---

# 03 — SITE PREPARATION

03.01 Site Clearing
03.02 Demolition
03.03 Temporary Facilities
03.04 Site Utilities
03.05 Temporary Power
03.06 Temporary Water
03.07 Site Access Roads
03.08 Surveying
03.09 Benchmark Establishment

---

# 04 — EARTHWORKS

04.01 Excavation
04.02 Soil Stabilization
04.03 Dewatering
04.04 Shoring
04.05 Retaining Systems
04.06 Backfilling
04.07 Soil Compaction
04.08 Earthwork Testing

---

# 05 — SUBSTRUCTURE

05.01 Lean Concrete
05.02 Waterproofing
05.03 Foundation Rebar
05.04 Foundation Formwork
05.05 Foundation Concrete
05.06 Raft Foundation
05.07 Footings
05.08 Pedestals
05.09 Basement Walls
05.10 Underground Slabs
05.11 Underground Utilities
05.12 Foundation Drainage

---

# 06 — SUPERSTRUCTURE

## 06.01 Concrete Structure

06.01.01 Columns
06.01.02 Shear Walls
06.01.03 Beams
06.01.04 Slabs
06.01.05 Stairs
06.01.06 Ramps
06.01.07 Roof Slabs
06.01.08 Structural Openings
06.01.09 Embedments
06.01.10 Concrete Curing

---

## 06.02 Steel Structure

06.02.01 Steel Columns
06.02.02 Steel Beams
06.02.03 Steel Connections
06.02.04 Decking
06.02.05 Structural Bolting
06.02.06 Structural Welding
06.02.07 Fireproofing

---

# 07 — ARCHITECTURAL WORKS

## 07.01 Masonry

07.01.01 Block Walls
07.01.02 Brick Walls
07.01.03 Shaft Walls
07.01.04 Partition Walls
07.01.05 Wall Reinforcement

---

## 07.02 Plaster & Surface Preparation

07.02.01 Internal Plaster
07.02.02 External Plaster
07.02.03 Surface Preparation
07.02.04 Waterproof Coating

---

## 07.03 Flooring

07.03.01 Screed
07.03.02 Tile Flooring
07.03.03 Stone Flooring
07.03.04 Epoxy Flooring
07.03.05 Raised Flooring
07.03.06 Floor Finishes

---

## 07.04 Ceiling Systems

07.04.01 Gypsum Ceiling
07.04.02 Acoustic Ceiling
07.04.03 Metal Ceiling
07.04.04 Ceiling Access Panels

---

## 07.05 Wall Finishes

07.05.01 Painting
07.05.02 Wall Cladding
07.05.03 Wallpaper
07.05.04 Decorative Finishes

---

## 07.06 Doors & Windows

07.06.01 Aluminum Windows
07.06.02 UPVC Windows
07.06.03 Glass Installation
07.06.04 Internal Doors
07.06.05 Fire Rated Doors
07.06.06 Hardware Installation

---

## 07.07 Facade Systems

07.07.01 Curtain Wall
07.07.02 Stone Facade
07.07.03 Metal Cladding
07.07.04 Facade Waterproofing
07.07.05 Facade Sealants
07.07.06 Facade Access Systems

---

# 08 — MECHANICAL WORKS

## 08.01 Plumbing

08.01.01 Domestic Water Piping
08.01.02 Drainage Piping
08.01.03 Vent Piping
08.01.04 Storm Water Piping
08.01.05 Plumbing Fixtures

---

## 08.02 HVAC

08.02.01 Ductwork
08.02.02 Pipework
08.02.03 Chillers
08.02.04 Cooling Towers
08.02.05 Air Handling Units
08.02.06 Fan Coil Units
08.02.07 Diffusers
08.02.08 Dampers
08.02.09 HVAC Insulation
08.02.10 HVAC Balancing

---

## 08.03 Fire Protection

08.03.01 Sprinkler Piping
08.03.02 Fire Pumps
08.03.03 Fire Cabinets
08.03.04 Fire Suppression Systems
08.03.05 Fire Protection Testing

---

# Final Architectural Principle

This WBS is intentionally:

* reusable
* scalable
* recursive
* operationally meaningful
* graph-compatible
* location-independent

Project-specific execution emerges dynamically through:

* locations
* workflows
* dependencies
* operational conditions
* execution states

NOT through hardcoded static schedules.
