# Runtime Bridge Design

Status: Draft

Version: 1.0

Purpose:

Define how BetavanX transitions from Planning into Operational Runtime.

This document describes the relationship between:

- Planning
- Activity Instances
- Workflow Steps
- Daily Work Orders
- Daily Reports
- Progress Tracking

---

# Problem Statement

BetavanX architecture defines:

WBS  

- 

Location  

- 

Workflow  
↓  
Activity Instance

However, runtime execution occurs through:

- Daily Work Orders
- Daily Reports
- Progress Tracking

A bridge is required between Planning and Runtime.

---

# Core Principle

Planning creates operational commitments.

Runtime measures execution against those commitments.

---

# Planning To Runtime Flow

Planning  
↓  
Activity Instance Creation  
↓  
Workflow Step Creation  
↓  
Daily Work Orders  
↓  
Daily Reports  
↓  
Progress Calculation  
↓  
Dashboard Visibility

---

# Activity Instance Creation

Activity Instances are created during Planning.

Creation Rule:

# WBS Item

- 

Location  

- 

Workflow Context

Activity Instance

Example:

WBS:  
Concrete Column

Location:  
Floor 3 / Axis C5

Result:

Activity Instance:  
Concrete Column C5

---

# Workflow Step Creation

Workflow Steps are automatically created when an Activity Instance is created.

Workflow Steps originate from the workflow definition attached to the activity type.

Example:

Activity Instance:

Concrete Column C5

Generated Workflow Steps:

- Rebar
- Formwork
- Concrete

Workflow Step creation is automatic.

Workflow Steps become operational entities immediately after creation.

---

# Work Order Generation

Daily Work Orders are generated from Workflow Steps.

A Daily Work Order may contain work from multiple Workflow Steps.

Example:

Daily Work Order  
2026-06-05

Included Items:

- Rebar C5
- Rebar C6
- Rebar C7
- Masonry W12

Daily Work Orders are execution packages.

Daily Work Orders are not operational truth.

Daily Work Orders are execution tools.

---

# Daily Reports

Daily Reports provide execution evidence.

Reports are submitted against Daily Work Orders.

Reports include:

- executed quantity
- manpower
- equipment
- delays
- notes
- photos
- issues

---

# Progress Model

Canonical Progress:

Physical Progress

Formula:

Executed Quantity  
/  
Planned Quantity

---

# Phase 1 Progress Truth

Workflow Step Progress is derived from:

Executed Quantity  
/  
Planned Quantity

Data Source:

Daily Reports

Validation Method:

Comparison against planned BOQ quantity.

Phase 1 assumes reports are entered by responsible execution personnel.

---

# Phase 2 Progress Evolution

Future versions may use multiple evidence sources.

Examples:

- Worker Reports
- Crew Reports
- Supervisor Reports
- Equipment Reports
- Sensor Data

Cross-validation may improve confidence.

However:

Canonical Progress remains:

Executed Quantity  
/  
Planned Quantity

Only confidence improves.

---

# Planning Accountability Principle

Planning creates commitments.

Every planned activity must be measurable against actual execution.

BetavanX records:

- Planned Quantity
- Planned Duration
- Planned Start
- Planned Finish

and compares them against:

- Actual Quantity
- Actual Duration
- Actual Start
- Actual Finish

The purpose is not punishment.

The purpose is accountability and planning quality measurement.

---

# Planning Accuracy

BetavanX evaluates:

Planned  
vs  
Actual

Metrics may include:

- Quantity Variance
- Duration Variance
- Start Variance
- Finish Variance

Planning quality becomes visible through execution evidence.

---

# Runtime Truth Hierarchy

Activity Instance  
↓  
Workflow Step  
↓  
Daily Work Order  
↓  
Daily Report

Operational truth originates from Activity Instances and Workflow Steps.

Daily Work Orders are execution tools.

Daily Reports are execution evidence.

---

# Dashboard Relationship

Dashboard metrics are derived from runtime execution.

Examples:

- Progress
- Delays
- Variances
- Productivity
- Planning Accuracy

Dashboards consume operational truth.

Dashboards do not create operational truth.

---

# Future Alignment

This model supports:

Construction Visibility  
↓  
Accountability  
↓  
Building Memory  
↓  
Building Trust

Execution evidence accumulates over time and contributes to the long-term intelligence layer of BetavanX.

---

## Dependency vs Blocker

Dependencies describe logical execution order.

Blockers describe temporary operational conditions.

Examples:

Dependency:

Formwork depends on Rebar completion.

Blocker:

Material shortage prevents execution even when dependencies are satisfied.

---

## Runtime Core Entities

The following entities are considered part of the Runtime Core:

- Activity Instance

- Workflow Step

- Inspection

- Approval

- Work Order

- Daily Report

- Blocker

---

## Future Entity Backlog

Future modeling work will include:

- Workflow Template

- Workflow Step Template

These entities define reusable execution patterns and generate Workflow Step instances during Activity Instance creation.

---
# Runtime Bridge Design

Status: Approved

Version: 2.0

---

# Purpose

Define how BetavanX transitions from Planning into Operational Runtime.

This document establishes the bridge between:

* Planning
* Activity Instances
* Workflow Steps
* Work Orders
* Daily Reports
* Progress Tracking

---

# Core Principle

Planning creates operational commitments.

Runtime measures execution against those commitments.

---

# Planning To Runtime Flow

Planning

↓

ActivityInstance Creation

↓

WorkflowStep Creation

↓

WorkOrder Generation

↓

Daily Report Submission

↓

Progress Calculation

↓

Inspection

↓

Approval

↓

Dashboard Visibility

---

# ActivityInstance Creation

ActivityInstances are created during Planning.

Creation Rule:

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

# WorkflowStep Creation

WorkflowSteps are automatically generated when an ActivityInstance is created.

WorkflowSteps originate from WorkflowStepTemplates.

Example:

ActivityInstance:

Column C5

↓

Generated WorkflowSteps:

* Rebar
* Formwork
* Concrete

WorkflowStep creation is automatic.

---

# WorkflowStep Snapshot Principle

WorkflowStepTemplate

↓

Snapshot

↓

WorkflowStep

WorkflowSteps preserve the execution knowledge that existed at creation time.

Templates may evolve later without affecting historical projects.

---

# WorkOrder Generation

WorkOrders are generated from WorkflowSteps.

WorkOrders represent daily execution commitments.

WorkOrders are execution slices.

WorkOrders are not operational truth.

---

# Example

WorkflowStep:

Rebar @ C5

↓

Generated WorkOrders:

WO-1

WO-2

WO-3

---

# WorkOrder Weight Principle

Workflow progress is distributed across WorkOrders.

Example:

WorkflowStep

Planned Quantity = 100 kg

↓

WO-1 = 33%

WO-2 = 33%

WO-3 = 34%

The percentages represent planning commitments.

The percentages do not necessarily represent measured physical quantities.

---

# Daily Reports

Daily Reports provide execution evidence.

Daily Reports are submitted against WorkOrders.

Daily Reports may contain:

* execution status
* notes
* photos
* manpower
* equipment
* issues
* delays
* weather observations

---

# WorkOrder Lifecycle

WorkOrder lifecycle:

Open

↓

In Progress

↓

Completed

or

Cancelled

A WorkOrder may remain In Progress across multiple days.

---

# Progress Model

Phase 1 Progress is commitment-based.

Progress is derived from completed WorkOrders.

---

# Formula

Workflow Progress

=

Σ Completed WorkOrder Weights

/

Total Workflow Weight

---

# Example

WO-1 Completed

↓

33%

WO-2 Completed

↓

66%

WO-3 Completed

↓

100%

---

# Why This Model

Physical quantity measurement is difficult to collect accurately in Phase 1.

Commitment completion is easier to verify and operationally practical.

This model maximizes adoption while preserving execution visibility.

---

# ActivityInstance Progress

ActivityInstances aggregate WorkflowStep progress.

Example:

Rebar = 100%

Formwork = 0%

Concrete = 0%

↓

ActivityInstance Progress = 33%

---

# Project Progress

Projects aggregate ActivityInstance progress.

Project visibility originates from execution reality.

---

# Inspection Flow

WorkflowStep

↓

Completed

↓

Inspection Pending

↓

Inspection

↓

Passed

or

Failed

---

# Failure Flow

Inspection Failed

↓

Punch Item Created

↓

Rework Required

↓

In Progress

↓

Reinspection

---

# Approval Flow

Phase 1 uses a simplified approval model.

WorkflowStep

↓

Inspection Passed

↓

Final Approval

↓

Approved

---

# Dashboard Relationship

Dashboards consume runtime truth.

Dashboards do not create runtime truth.

Examples:

* progress
* delays
* blockers
* inspections
* approvals
* planning accuracy

---

# Planning Accountability

Planning creates commitments.

Runtime measures actual execution against those commitments.

BetavanX records:

* planned duration
* planned start
* planned finish
* planned workflow commitments

and compares them against:

* actual execution
* actual completion
* actual approvals

---

# Future Evolution

Future versions may introduce:

* physical quantity tracking
* BIM validation
* AI validation
* image-based quantity estimation
* resource consumption tracking
* automated progress verification

Phase 1 intentionally focuses on operational simplicity.

---

# Runtime Truth Hierarchy

ActivityInstance

↓

WorkflowStep

↓

WorkOrder

↓

DailyReport

↓

Progress

↓

Inspection

↓

Approval

Runtime execution is measured against planning commitments.

This bridge connects Planning Reality to Operational Reality.

---

# Strategic Alignment

Planning

↓

Execution

↓

Measurement

↓

Visibility

↓

Accountability

↓

Building Memory

↓

Building Intelligence

↓

Building Trust

This Runtime Bridge is the operational backbone of BetavanX Phase 1.
