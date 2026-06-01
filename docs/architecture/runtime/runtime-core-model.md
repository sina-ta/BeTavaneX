# Runtime Core Model

Status: Approved

Version: 1.1

---

# Purpose

Define the Runtime Core of BetavanX Phase 1.

This document establishes the canonical runtime entities and their relationships.

The Runtime Core represents operational reality during project execution.

---

# Core Principle

BetavanX does not model execution through generic tasks.

BetavanX models execution through construction reality.

The Runtime Core is organized around:

Construction Reality

↓

Execution Reality

↓

Execution Evidence

---

# Runtime Layers

## Construction Reality

Construction Reality is represented by:

ActivityInstance

Examples:

* Column C5
* Wall W12
* Slab S3

ActivityInstances represent actual scopes of construction work.

---

## Execution Reality

Execution Reality is represented by:

WorkflowStep

Examples:

* Rebar
* Formwork
* Concrete

WorkflowSteps represent measurable execution stages required to complete an ActivityInstance.

WorkflowSteps are the primary operational entities of BetavanX.

---

## Execution Knowledge

Execution Knowledge is represented by:

WorkflowStepTemplate

Examples:

* Rebar Template
* Formwork Template
* Concrete Template

WorkflowStepTemplates define reusable execution knowledge.

WorkflowSteps are instantiated from WorkflowStepTemplate snapshots.

WorkflowSteps do not maintain live references to templates.

Template changes do not affect existing WorkflowSteps.

---

## Execution Coordination

Execution Coordination is represented by:

WorkOrder

WorkOrders define daily execution commitments.

WorkOrders do not represent operational truth.

WorkOrders are execution coordination tools.

---

## Execution Evidence

Execution Evidence is represented by:

DailyReport

DailyReports record execution outcomes.

DailyReports provide evidence of execution.

---

## Quality Verification

Quality Verification is represented by:

Inspection

Inspections verify execution quality.

---

## Quality Findings

Quality Findings are represented by:

PunchItem

PunchItems record deficiencies discovered during inspections.

---

## Operational Approval

Operational Approval is represented by:

Approval

Phase 1 uses a simplified approval model.

A single final approval confirms workflow completion.

---

## Operational Constraints

Operational Constraints are represented by:

Blocker

Blockers represent unexpected conditions preventing execution.

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

# Supporting Runtime Entities

The following entities support Runtime operations but are not considered Runtime Core:

* BOQMapping

BOQMapping provides the linkage between execution reality and financial measurement reality.

---

# Entity Relationships

ActivityInstance

1:N

WorkflowStep

---

WorkflowStepTemplate

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

WorkflowStep

1:N

Blocker

---

WorkflowStep

1:N

BOQMapping

---

# Runtime Truth Hierarchy

ActivityInstance

↓

WorkflowStep

↓

DailyReport

Operational truth originates from:

* ActivityInstances
* WorkflowSteps

DailyReports provide execution evidence.

WorkOrders do not create operational truth.

---

# Ownership Principles

## ActivityInstance Owns

* construction scope
* planning commitment
* aggregated progress
* aggregated planned cost

---

## WorkflowStep Owns

* execution state
* progress
* inspections
* approvals
* blockers
* work orders
* assigned resources
* assigned crews
* assigned contractors
* assigned supervisors
* BOQ mappings

---

## WorkOrder Owns

* daily execution commitment

WorkOrders do not own:

* progress
* resources
* costs
* inspections
* approvals

---

## DailyReport Owns

* execution evidence

---

## Inspection Owns

* quality verification

---

## PunchItem Owns

* quality deficiencies

---

## Approval Owns

* final execution approval

---

## Blocker Owns

* unexpected operational constraints

---

# Runtime Philosophy

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

---

Financial Measurement Reality

↓

BOQItem

↓

BOQMapping

↓

WorkflowStep

---

# Runtime Principles

## Progress Principle

WorkflowSteps own progress.

WorkOrders contribute to progress.

WorkOrders do not own progress.

---

## Approval Principle

Progress and Approval are independent concepts.

A WorkflowStep may reach:

Progress = 100%

while remaining:

Inspection Pending

or

Approval Pending

---

## Template Principle

Templates define knowledge.

WorkflowSteps preserve historical execution reality through snapshot creation.

---

# Strategic Alignment

The Runtime Core supports:

Construction Visibility

↓

Operational Accountability

↓

Building Memory

↓

Building Trust

The Runtime Core forms the operational foundation of BetavanX Phase 1.
