# Relationship Matrix

Status: Approved

Version: 1.0

Purpose:

Define the canonical relationships between BetavanX entities.

This document serves as the primary reference for:

- Data Dictionary
- ERD Design
- Database Design
- API Design

---

# Planning Layer

## Project → WBSItem

Project

1:N

WBSItem

A project contains multiple WBS items.

---

## Project → Location

Project

1:N

Location

A project contains multiple locations.

---

## Project → BOQItem

Project

1:N

BOQItem

A project contains multiple BOQ items.

---

## WBSItem → ActivityInstance

WBSItem

1:N

ActivityInstance

A WBS item may generate multiple ActivityInstances.

Example:

Concrete Column

↓

Column C1

Column C2

Column C3

---

## Location → ActivityInstance

Location

1:N

ActivityInstance

A location may contain multiple ActivityInstances.

---

# Construction Reality Layer

## ActivityInstance → WorkflowStep

ActivityInstance

1:N

WorkflowStep

A construction scope may contain multiple execution stages.

Example:

Column C5

↓

Rebar

Formwork

Concrete

---

# Execution Knowledge Layer

## WorkflowStepTemplate → WorkflowStep

WorkflowStepTemplate

1:N

WorkflowStep

Relationship Type:

Snapshot Creation

WorkflowSteps are instantiated from template snapshots.

WorkflowSteps do not maintain live references to templates.

Template changes do not affect historical WorkflowSteps.

---

# Execution Coordination Layer

## WorkflowStep → WorkOrder

WorkflowStep

N:N

WorkOrder

A WorkflowStep may be executed through multiple WorkOrders.

Example:

Rebar @ C5

↓

WO-1

WO-2

WO-3

---

## WorkOrder → DailyReport

WorkOrder

1:N

DailyReport

A WorkOrder may generate multiple DailyReports.

DailyReports provide execution evidence.

---

# Quality Layer

## WorkflowStep → Inspection

WorkflowStep

1:N

Inspection

A WorkflowStep may have multiple inspections.

---

## Inspection → PunchItem

Inspection

1:N

PunchItem

An inspection may identify multiple quality issues.

---

## WorkflowStep → Approval

WorkflowStep

1:N

Approval

A WorkflowStep may have multiple approvals over time.

Phase 1 typically uses a single final approval.

---

# Operational Constraint Layer

## WorkflowStep → Blocker

WorkflowStep

1:N

Blocker

A WorkflowStep may experience multiple operational constraints.

---

# Financial Layer

## WorkflowStep → BOQMapping

WorkflowStep

1:N

BOQMapping

A WorkflowStep may have multiple BOQ allocations.

---

## BOQItem → BOQMapping

BOQItem

1:N

BOQMapping

A BOQItem may be distributed across multiple WorkflowSteps.

---

# Resource Layer

## WorkflowStep → Resource

WorkflowStep

N:N

Resource

Resources may participate in multiple WorkflowSteps.

---

## WorkflowStep → Crew

WorkflowStep

N:N

Crew

Crews may participate in multiple WorkflowSteps.

---

## WorkflowStep → Equipment

WorkflowStep

N:N

Equipment

Equipment may participate in multiple WorkflowSteps.

---

## WorkflowStep → Material

WorkflowStep

N:N

Material

Materials may be consumed across multiple WorkflowSteps.

---

## WorkflowStep → Contractor

WorkflowStep

N:1

Contractor

A WorkflowStep is typically assigned to one responsible contractor.

A contractor may execute multiple WorkflowSteps.

---

## WorkflowStep → Supervisor

WorkflowStep

N:1

Supervisor

A WorkflowStep is typically assigned to one responsible supervisor.

A supervisor may oversee multiple WorkflowSteps.

---

# Runtime Hierarchy

Project

↓

ActivityInstance

↓

WorkflowStep

↓

WorkOrder

↓

DailyReport

---

# Quality Hierarchy

WorkflowStep

↓

Inspection

↓

PunchItem

---

WorkflowStep

↓

Approval

---

# Constraint Hierarchy

WorkflowStep

↓

Blocker

---

# Financial Hierarchy

Project

↓

BOQItem

↓

BOQMapping

↓

WorkflowStep

---

# Knowledge Hierarchy

WorkflowStepTemplate

↓

WorkflowStep Snapshot

---

# Relationship Summary


| Parent               | Relationship | Child            |
| -------------------- | ------------ | ---------------- |
| Project              | 1:N          | WBSItem          |
| Project              | 1:N          | Location         |
| Project              | 1:N          | BOQItem          |
| WBSItem              | 1:N          | ActivityInstance |
| Location             | 1:N          | ActivityInstance |
| ActivityInstance     | 1:N          | WorkflowStep     |
| WorkflowStepTemplate | 1:N          | WorkflowStep     |
| WorkflowStep         | N:N          | WorkOrder        |
| WorkOrder            | 1:N          | DailyReport      |
| WorkflowStep         | 1:N          | Inspection       |
| Inspection           | 1:N          | PunchItem        |
| WorkflowStep         | 1:N          | Approval         |
| WorkflowStep         | 1:N          | Blocker          |
| WorkflowStep         | 1:N          | BOQMapping       |
| BOQItem              | 1:N          | BOQMapping       |
| WorkflowStep         | N:N          | Resource         |
| WorkflowStep         | N:N          | Crew             |
| WorkflowStep         | N:N          | Equipment        |
| WorkflowStep         | N:N          | Material         |
| WorkflowStep         | N:1          | Contractor       |
| WorkflowStep         | N:1          | Supervisor       |


---

# Architectural Principle

BetavanX separates:

Construction Reality

↓

ActivityInstance

---

Execution Reality

↓

WorkflowStep

---

Execution Coordination

↓

WorkOrder

---

Execution Evidence

↓

DailyReport

---

Financial Reality

↓

BOQItem

---

Integration Layer

↓

BOQMapping

---

Quality Verification

↓

Inspection

↓

PunchItem

---

Operational Approval

↓

Approval

---

Operational Constraints

↓

Blocker

This relationship model forms the foundation of the BetavanX database architecture.