# Workflow Step Domain Model

Status: Accepted

Version: 1.0

Purpose:

Define the operational execution model of Workflow Steps within BetavanX.

Workflow Steps are the primary execution management entities of the platform.

Workflow Steps belong to Activity Instances and represent executable construction stages.

---

# Core Principle

Activity Instance represents construction reality.

Workflow Step represents execution management reality.

Daily Work Order represents daily execution instructions.

Daily Report represents execution evidence.

Workflow Step is the smallest operational unit that can be:

- planned
- executed
- monitored
- blocked
- approved
- inspected
- measured
- analyzed

---

# Relationship to Activity Instance

Activity Instance  
1  
↓  
N

Workflow Steps

Example:

Activity Instance:

Concrete Column C5

Workflow Steps:

1. Rebar
2. Formwork
3. Concrete

Workflow Steps belong to a single Activity Instance.

An Activity Instance owns its complete execution workflow.

---

# Workflow Step Definition

A Workflow Step represents an executable stage of construction work.

Examples:

- Rebar
- Formwork
- Concrete
- Waterproofing
- Masonry
- MEP Rough-In

Workflow Steps are operational entities.

They are not merely labels or workflow definitions.

---

# Workflow Step Responsibilities

Workflow Step owns:

- execution status
- progress
- dependencies
- readiness evaluation
- blockers
- inspections
- approvals
- quality records
- assigned resources
- work orders
- execution history

---

# Workflow Step Lifecycle

Workflow Step lifecycle:

Planned  
↓  
In Progress  
↓  
Completed  
↓  
Approval Pending

Approval Pending  
├── Approved  
└── Inspection Failed  
↓  
Rework Required  
↓  
In Progress

---

# Lifecycle Definitions

## Planned

Workflow Step exists but execution has not started.

---

## In Progress

Execution has started.

Daily Work Orders and Daily Reports may exist.

Physical progress is increasing.

---

## Completed

Physical work has been completed.

Completed means:

Physical Work Finished

Completed does NOT mean approved.

---

## Approval Pending

Physical work is complete.

Inspection and approval process is waiting.

---

## Inspection Failed

Inspection has failed.

Workflow Step cannot progress to Approved.

Punch Items may be created.

Rework may be required.

---

## Rework Required

Corrective actions are required.

The Workflow Step returns to execution.

After rework:

Rework Required  
↓  
In Progress  
↓  
Completed  
↓  
Approval Pending

---

## Approved

Inspection completed successfully.

Approval granted.

Workflow Step is accepted.

Dependent Workflow Steps may proceed.

---

# Progress Model

Canonical Progress:

Physical Progress

Progress is based on:

Completed Quantity  
/  
Planned Quantity

Examples:

120 m² Wall

60 m² Completed

Progress = 50%

---

# Progress Aggregation

Daily Reports  
↓  
Workflow Step Progress  
↓  
Activity Instance Progress

Workflow Step Progress is the primary execution progress unit.

---

# Readiness Model

Readiness is NOT a lifecycle state.

Readiness is a computed condition.

A Workflow Step becomes executable only when readiness conditions are satisfied.

---

# Readiness Conditions

Dependency Ready

Approval Ready

Material Ready

Crew Ready

Equipment Ready

Location Ready

Constraint Free

---

# Readiness Evaluation

Ready = True

only when:

Dependency Ready  
AND

Approval Ready  
AND

Material Ready  
AND

Crew Ready  
AND

Equipment Ready  
AND

Location Ready  
AND

Constraint Free

---

# Dependency Model

Workflow Steps may depend on multiple dependency types.

---

## Workflow Dependency

Dependency on another Workflow Step within the same Activity Instance.

Example:

Rebar  
↓  
Formwork  
↓  
Concrete

---

## Activity Instance Dependency

Dependency on another Activity Instance.

Examples:

Column depends on Foundation

MEP Installation depends on Structural Completion

---

## Approval Dependency

Dependency on required approvals.

Examples:

Formwork depends on Rebar Approval.

Concrete depends on Formwork Approval.

---

## Location Dependency

Dependency on location readiness.

Examples:

Area access

Workfront availability

Location release

---

## External Dependency

Dependency outside the operational graph.

Examples:

Permit Approval

Material Delivery

Equipment Arrival

Weather Conditions

Owner Decisions

Utility Availability

---

# Dependency Resolution Rule

A Workflow Step becomes executable only when all required dependencies are satisfied.

Dependencies affect readiness.

Dependencies do not directly change lifecycle status.

---

# Resource Model

Workflow Steps define required resources.

Examples:

- manpower
- equipment
- materials

Resource requirements are defined at Workflow Step level.

Actual daily allocation occurs through Daily Work Orders.

---

# Work Order Relationship

Workflow Step  
1  
↓  
N

Daily Work Orders

Daily Work Orders are daily execution instructions.

A Workflow Step may generate multiple Daily Work Orders across multiple days.

Example:

Workflow Step:

Rebar

Work Orders:

Day 1  
Install Rebar

Day 2  
Continue Rebar

Day 3  
Finish Rebar

---

# Daily Report Relationship

Daily Work Order  
1  
↓  
N

Daily Reports

Daily Reports represent execution evidence.

Examples:

- quantities
- manpower
- equipment usage
- delays
- notes
- photos
- attachments

---

# Inspection Model

Workflow Steps may have multiple inspections.

Workflow Step  
1  
↓  
N

Inspections

Examples:

- Rebar Inspection
- Formwork Inspection
- Concrete Inspection

Inspections determine whether work may proceed toward approval.

---

# Approval Model

Workflow Steps may require approval.

Approvals occur after physical completion.

Examples:

- Consultant Approval
- Client Approval
- Internal Approval
- Quality Approval

Approvals may unlock dependent Workflow Steps.

---

# Punch List Model

Inspection failures may create Punch Items.

Workflow Step  
1  
↓  
N

Punch Items

Examples:

- Cover Thickness Violation
- Formwork Alignment Issue
- Honeycomb Repair

Punch Items must be resolved before approval.

---

# Blocker Model

Blockers are independent operational entities.

Blockers prevent execution even when readiness conditions appear satisfied.

Examples:

- Material Shortage
- Equipment Failure
- Access Restriction
- Safety Stop
- Permit Delay
- Weather Event

Workflow Step  
1  
↓  
N

Blockers

---

# Ownership Model

BetavanX supports both hierarchical and single-user operation.

---

## Hierarchical Example

Technical Office  
↓  
Creates WBS Templates

Project Manager  
↓  
Creates Activity Instances

Site Supervisor  
↓  
Defines Workflow Execution

Execution Teams  
↓  
Execute Daily Work Orders

---

## Single User Example

One person may perform all roles.

Ownership defines responsibility.

Ownership does not require organizational complexity.

---

# Execution Quality History

Workflow Steps maintain complete quality history.

Quality history is immutable.

Workflow Step quality history includes:

- inspections
- failed inspections
- approvals
- punch items
- rework cycles
- corrective actions

Inspection failure does not create a new Workflow Step.

The same Workflow Step remains active.

Examples:

Inspection #1  
Failed

Punch Items Created

Rework Performed

Inspection #2  
Passed

Approval Granted

All events remain attached to the same Workflow Step.

---

# Future Intelligence Value

Workflow Step history enables:

- contractor performance scoring
- crew performance scoring
- inspection pass rate analysis
- rework analysis
- quality scoring
- productivity analysis
- trust indicators

This history contributes to:

Construction Visibility  
↓  
Building Memory  
↓  
Building Trust

---

# Runtime Meaning

Activity Instance answers:

"What exists in the building?"

Workflow Step answers:

"What execution stage are we in?"

Daily Work Order answers:

"What should be done today?"

Daily Report answers:

"What actually happened today?"

---

# Canonical Runtime Hierarchy

Activity Instance  
1  
↓  
N

Workflow Steps  
1  
↓  
N

Daily Work Orders  
1  
↓  
N

Daily Reports

---

# Design Decisions

Workflow Step is a first-class operational entity.

Readiness is a computed condition, not a state.

Progress is physical progress, not financial progress.

Completed is different from Approved.

Inspection failures reopen execution through rework.

Blockers are independent entities.

Workflow Step quality history must be preserved permanently.