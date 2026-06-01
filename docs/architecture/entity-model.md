# BetavanX Entity Model

Status: Approved

Version: 1.0

Purpose:

Define the canonical entity structure of BetavanX.

This document describes the major entities of the system and their relationships.

Detailed business rules are documented in dedicated domain model documents.

---

# Architectural Layers

BetavanX entities are organized into:

1. Planning Layer

2. Execution Knowledge Layer

3. Execution Layer

4. Quality Layer

5. Operational Constraint Layer

6. Resource Layer

---

# Planning Layer

Entities:

* Project
* WBSItem
* Location
* BOQItem
* ActivityInstance

---

## Relationships

Project

1:N

WBSItem

---

Project

1:N

Location

---

Project

1:N

BOQItem

---

WBSItem

1:N

ActivityInstance

---

Location

1:N

ActivityInstance

---

# Execution Knowledge Layer

Entities:

* WorkflowStepTemplate

---

## Relationships

WorkflowStepTemplate

1:N

WorkflowStep

---

# Execution Layer

Entities:

* ActivityInstance
* WorkflowStep
* WorkOrder
* DailyReport

---

## Relationships

ActivityInstance

1:N

WorkflowStep

---

WorkflowStep

1:N

WorkOrder

---

WorkOrder

1:N

DailyReport

---

# Quality Layer

Entities:

* Inspection
* PunchItem
* Approval

---

## Relationships

WorkflowStep

1:N

Inspection

---

Inspection

1:N

PunchItem

---

WorkflowStep

1:N

Approval

---

# Operational Constraint Layer

Entities:

* Blocker

---

## Relationships

WorkflowStep

1:N

Blocker

---

# Resource Layer

Entities:

* Resource
* Crew
* Contractor
* Supervisor
* Equipment
* Material

---

## Relationships

WorkflowStep

N:N

Resource

---

WorkflowStep

N:N

Crew

---

WorkflowStep

N:N

Equipment

---

WorkflowStep

N:N

Material

---

WorkflowStep

N:1

Contractor

---

WorkflowStep

N:1

Supervisor

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

# Approval Hierarchy

WorkflowStep

↓

Approval

---

# Knowledge Hierarchy

WorkflowStepTemplate

↓

WorkflowStep

---

# Runtime Core Entities

The Runtime Core consists of:

* ActivityInstance
* WorkflowStepTemplate
* WorkflowStep
* WorkOrder
* DailyReport
* Inspection
* PunchItem
* Approval
* Blocker

---

# Planning Core Entities

The Planning Core consists of:

* Project
* WBSItem
* Location
* BOQItem
* ActivityInstance

---

# Resource Core Entities

The Resource Core consists of:

* Resource
* Crew
* Contractor
* Supervisor
* Equipment
* Material

---

# Future Backlog Entities

Future versions may introduce:

* BIMElement
* Permit
* Document
* ResourceCatalog
* CostRecord
* CostIntelligence
* MultiStageApproval
* KnowledgeRecommendation
* AIPlanningRecommendation

---

# Architectural Principle

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

Execution Knowledge

↓

WorkflowStepTemplate

---

Quality Verification

↓

Inspection

↓

PunchItem

---

Operational Constraints

↓

Blocker

---

Operational Approval

↓

Approval

---

# Scope

This document defines:

* entity existence
* entity boundaries
* entity relationships

This document does not define:

* business rules
* lifecycle logic
* progress calculations
* approval logic
* cost calculations

Those concerns are documented in dedicated domain model documents.
