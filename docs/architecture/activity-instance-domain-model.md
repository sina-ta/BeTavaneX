# Activity Instance Domain Model

Status: Accepted

Version: 2.0

Purpose:

Define the canonical operational execution model of BetavanX.

This document defines:

- Activity Instance
- Workflow Step
- Daily Work Order
- Daily Report

and the relationships between them.

---

# Core Principle

Construction reality is represented by Activity Instances.

Execution reality is represented by Workflow Steps.

Operational execution is managed through Daily Work Orders.

Execution evidence is captured through Daily Reports.

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

# Activity Instance

## Definition

An Activity Instance represents a real construction activity at a specific location.

Activity Instances are created during Planning.

Creation occurs when:

WBS Item  
+  
Location

become a real planned construction activity.

---

## Examples

Concrete Column C5

Masonry Wall W12

HVAC Zone A-03

Fire Alarm Loop B

---

## Characteristics

Activity Instance:

- represents construction reality
- has physical location
- has measurable quantity
- has lifecycle history
- owns workflow execution
- owns overall progress

Activity Instance is NOT:

- schedule
- workflow step
- work order
- daily report

---

## Example

Activity Instance

Name:  
Concrete Column C5

Location:  
Floor 3

Quantity:  
8 m³

Status:  
In Progress

---

# Workflow Step

## Definition

Workflow Step represents an executable operational stage within an Activity Instance.

Workflow Steps are first-class operational entities.

Workflow Steps are NOT labels.

Workflow Steps are independently managed execution units.

---

## Example

Activity Instance:

Concrete Column C5

Workflow Steps:

1. Rebar
2. Formwork
3. Concrete

---

## Why Workflow Step Is An Entity

Workflow Steps may have:

- status
- approvals
- blockers
- readiness checks
- dependencies
- resource requirements
- progress
- inspections
- quality checks
- actual start dates
- actual finish dates

Because Workflow Steps have independent operational state, they must be modeled as entities.

---

## Example

Workflow Step:

Rebar

Status:  
Completed

Approval:  
Approved

Progress:  
100%

Actual Start:  
2026-06-01

Actual Finish:  
2026-06-03

---

# Workflow Dependencies

Workflow execution follows defined sequence.

Example:

Rebar  
↓  
Formwork  
↓  
Concrete

Formwork cannot start until:

Rebar is completed  
AND  
Rebar approval is granted

Concrete cannot start until:

Formwork is completed  
AND  
Formwork approval is granted

---

# Workflow Step Characteristics

Workflow Step owns:

- execution status
- readiness state
- blockers
- approvals
- progress
- assigned resources
- quality records

Workflow Step may generate multiple Daily Work Orders.

---

# Daily Work Order

## Definition

Daily Work Orders are daily execution instructions.

Daily Work Orders belong to Workflow Steps.

Daily Work Orders are not operational truth.

Daily Work Orders are operational instructions.

---

## Example

Workflow Step:

Rebar

Daily Work Orders:

Day 1:  
Install Rebar

Day 2:  
Continue Rebar

Day 3:  
Finish Rebar

---

## Characteristics

Daily Work Orders:

- are date specific
- are crew specific
- are resource specific
- define daily targets
- define daily execution plans

---

# Daily Report

## Definition

Daily Reports represent execution evidence.

Daily Reports belong to Daily Work Orders.

Daily Reports capture actual field execution.

---

## Example

Daily Report

Date:  
2026-06-01

Work Order:  
Install Rebar

Manpower:  
8

Completed Quantity:  
1.5 tons

Weather:  
Clear

---

## Daily Reports May Include

- quantities
- manpower
- equipment
- notes
- issues
- photos
- attachments
- inspection records

---

# Progress Model

Progress is derived from Daily Reports.

Progress aggregation:

Daily Reports  
→ Workflow Step Progress  
→ Activity Instance Progress

---

## Example

Activity Instance:

Concrete Column C5

Workflow Steps:

Rebar:  
100%

Formwork:  
100%

Concrete:  
50%

Activity Progress:  
83%

---

# Scheduling Relationship

Activity Instances exist before scheduling.

Workflow Steps exist before scheduling.

Scheduling operates on:

- Activity Instances
- Workflow Steps

Scheduling determines:

- start dates
- finish dates
- sequencing
- resource allocation

Scheduling does not create Activity Instances.

Scheduling does not create Workflow Steps.

---

# Resource Relationship

Resources are assigned primarily to Workflow Steps and Daily Work Orders.

Examples:

- crews
- equipment
- materials

Workflow Steps may define required resources.

Daily Work Orders define actual daily resource assignments.

---

# Approval Model

Approvals occur at Workflow Step level.

Examples:

Rebar Approval

Formwork Approval

Concrete Approval

Workflow progression may depend on approval completion.

---

# Quality Model

Quality inspections occur at Workflow Step level.

Examples:

Rebar Inspection

Formwork Inspection

Concrete Strength Test

Quality records belong to Workflow Steps.

---

# Building Memory Relationship

Building Memory is built around Activity Instances.

Workflow execution history is preserved through Workflow Steps.

Future lifecycle records may connect to:

- Activity Instance
- Workflow Step

Examples:

- inspections
- defects
- warranties
- maintenance history
- repair history
- renovation history

---

# Runtime Truth Model

Operational Truth:

Activity Instance  
↓  
Workflow Step  
↓  
Daily Work Order  
↓  
Daily Report

---

# Runtime Meaning

Activity Instance

Answers:

"What exists in the building?"

---

Workflow Step

Answers:

"What stage of execution are we in?"

---

Daily Work Order

Answers:

"What should be done today?"

---

Daily Report

Answers:

"What actually happened today?"

---

# Example

Activity Instance

Concrete Column C5

↓

Workflow Step

Rebar

↓

Work Orders

Install Rebar  
Continue Rebar  
Finish Rebar

↓

Daily Reports

Report 1  
Report 2  
Report 3

↓

Progress

Rebar = 100%

↓

Workflow Continues

Formwork

↓

Concrete

---

# Open Questions

1. Workflow Step lifecycle state machine
2. Approval state machine
3. Dependency model between Activity Instances
4. Dependency model between Workflow Steps
5. Progress weighting model
6. Resource capacity model
7. Runtime migration path from DailyWorkOrder-centric runtime to ActivityInstance-centric runtime

