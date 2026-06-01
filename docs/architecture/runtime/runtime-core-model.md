# Runtime Core Model

Status: Approved

Version: 1.0

---

# Purpose

Define the Runtime Core of BetavanX Phase 1.

This document establishes the canonical runtime entities and their relationships.

The Runtime Core represents operational reality during project execution.

---

# Core Principle

BetavanX does not model execution through tasks.

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

- Column C5
- Wall W12
- Slab S3

ActivityInstances represent actual scopes of construction work.

---

## Execution Reality

Execution Reality is represented by:

WorkflowStep

Examples:

- Rebar
- Formwork
- Concrete

WorkflowSteps represent measurable execution stages required to complete an ActivityInstance.

---

## Execution Knowledge

Execution Knowledge is represented by:

WorkflowStepTemplate

Examples:

- Rebar Template
- Formwork Template
- Concrete Template

WorkflowStepTemplates define reusable execution knowledge.

---

## Execution Coordination

Execution Coordination is represented by:

WorkOrder

WorkOrders define daily execution commitments.

WorkOrders do not represent operational truth.

WorkOrders are execution tools.

---

## Execution Evidence

Execution Evidence is represented by:

DailyReport

DailyReports record execution outcomes.

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

- ActivityInstance
- WorkflowStepTemplate
- WorkflowStep
- WorkOrder
- DailyReport
- Inspection
- PunchItem
- Approval
- Blocker

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

# Runtime Truth Hierarchy

ActivityInstance  
↓  
WorkflowStep  
↓  
DailyReport

Operational truth originates from ActivityInstances and WorkflowSteps.

DailyReports provide execution evidence.

WorkOrders do not create operational truth.

---

# Ownership Principles

ActivityInstance owns:

- construction scope
- planning commitment

---

WorkflowStep owns:

- execution state
- progress
- inspections
- approvals
- blockers
- assigned resources
- assigned crews
- assigned contractors
- assigned supervisors

---

WorkOrder owns:

- daily execution commitment

WorkOrders do not own resources.

WorkOrders do not own progress.

WorkOrders do not own costs.

---

DailyReport owns:

- execution evidence

---

Inspection owns:

- quality verification

---

PunchItem owns:

- quality deficiencies

---

Approval owns:

- final execution approval

---

Blocker owns:

- unexpected operational constraints

---

# Runtime Philosophy

Construction Reality  
↓  
ActivityInstance

Execution Reality  
↓  
WorkflowStep

Execution Coordination  
↓  
WorkOrder

Execution Evidence  
↓  
DailyReport

Quality Verification  
↓  
Inspection

Quality Findings  
↓  
PunchItem

Operational Approval  
↓  
Approval

Operational Constraints  
↓  
Blocker

---

# Strategic Alignment

This Runtime Core supports:

Construction Visibility  
↓  
Operational Accountability  
↓  
Building Memory  
↓  
Building Trust

The Runtime Core forms the foundation of BetavanX Phase 1.