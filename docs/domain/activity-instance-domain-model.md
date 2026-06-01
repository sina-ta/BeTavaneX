# Activity Instance Domain Model

Status: Approved

Version: 1.1

---

# Purpose

Define the canonical construction reality entity of BetavanX.

ActivityInstance represents a specific construction scope at a specific location together with its planning commitment.

ActivityInstance is the primary construction reality entity.

---

# Definition

ActivityInstance

=

Construction Scope

*

Planning Commitment

---

# Examples

Examples of ActivityInstances:

* Column C5
* Column C6
* Wall W12
* Slab S3
* Footing F8

Each ActivityInstance represents a unique physical construction scope.

---

# Core Principle

ActivityInstances are created during Planning.

Planning creates operational commitments.

Runtime measures execution against those commitments.

---

# Creation Rule

ActivityInstance is created when:

WBS Item

*

Location

↓

ActivityInstance

---

# Example

WBS Item:

Concrete Column

Location:

Floor 3 / Axis C5

↓

ActivityInstance:

Column C5

---

# Planning Ownership

ActivityInstance owns planning commitments.

Examples:

* planned quantity
* planned duration
* planned start
* planned finish

---

# Construction Scope Ownership

ActivityInstance owns:

* construction scope definition
* location assignment
* planning commitment
* aggregated execution progress
* aggregated execution cost

---

# Relationships

## Project Relationship

Project

1:N

ActivityInstance

A project contains many ActivityInstances.

---

## WBS Relationship

WBS Item

1:N

ActivityInstance

A WBS Item may create many ActivityInstances.

Example:

Concrete Column

↓

Column C1

Column C2

Column C3

---

## Location Relationship

Location

1:N

ActivityInstance

A location may contain multiple ActivityInstances.

---

## Workflow Relationship

ActivityInstance

1:N

WorkflowStep

WorkflowSteps execute an ActivityInstance.

---

# BOQ Relationship

BOQ is NOT owned by ActivityInstance.

---

Incorrect:

ActivityInstance

→ BOQ

---

Correct:

ActivityInstance

↓

WorkflowStep

↓

BOQ Mapping

↓

BOQ Item

---

Reason:

Construction scope and financial measurement are different concepts.

ActivityInstance represents construction reality.

BOQ represents financial measurement reality.

---

# Progress Aggregation

ActivityInstance does not create progress.

WorkflowSteps create progress.

ActivityInstance aggregates progress from WorkflowSteps.

---

# ActivityInstance Progress

Phase 1 uses Planning Weights.

Each WorkflowStep receives a planning weight during planning.

Example:

Rebar = 20%

Formwork = 30%

Concrete = 50%

---

ActivityInstance Progress

=

Σ WorkflowStep Progress × WorkflowStep Weight

---

Example

Rebar Progress = 100%

Formwork Progress = 0%

Concrete Progress = 0%

↓

ActivityInstance Progress = 20%

---

# Cost Aggregation

WorkflowStep planned cost originates from BOQ mappings.

ActivityInstance aggregates planned costs from WorkflowSteps.

ActivityInstance does not directly own BOQItems.

---

# Lifecycle Responsibility

ActivityInstance is responsible for:

* defining construction scope
* defining planning commitments
* aggregating execution progress
* aggregating execution cost
* aggregating execution status

ActivityInstance is NOT responsible for:

* daily execution
* inspections
* approvals
* blockers

These belong to WorkflowSteps.

---

# Activity Instance Repetition

ActivityInstances are unique per location.

Example:

Concrete Column

↓

Column C1

Column C2

Column C3

Each is a separate ActivityInstance.

ActivityInstances are never reused across locations.

---

# Runtime Position

Construction Reality

↓

ActivityInstance

↓

Execution Reality

↓

WorkflowStep

↓

Execution Evidence

↓

DailyReport

ActivityInstance is the bridge between Planning and Execution.

---

# Strategic Alignment

ActivityInstance represents the digital identity of a construction scope.

Over time ActivityInstances contribute to:

Construction Visibility

↓

Building Memory

↓

Building Intelligence

↓

Building Trust

ActivityInstance is the foundation of construction reality inside BetavanX.
