# Entity Catalog

Status: Draft

Version: 1.0

---

# ActivityInstance

## Purpose

Represents a specific construction scope at a specific location together with its planning commitment.

ActivityInstance is the canonical construction reality entity of BetavanX.

---

## Layer

Construction Reality

---

## Owner

Planning Layer

---

## Definition

ActivityInstance

=

Construction Scope

- 

Planning Commitment

---

## Creation Rule

WBS Item

- 

Location

↓

ActivityInstance

Example:

Concrete Column

- 

Floor 3 / Axis C5

↓

Column C5

---

## Lifecycle

Active

↓

Completed

or

Cancelled

---

## Relationships

### Project

N:1

An ActivityInstance belongs to a single Project.

---

### WBSItem

N:1

An ActivityInstance originates from a WBSItem.

---

### Location

N:1

An ActivityInstance is assigned to a Location.

---

### WorkflowStep

1:N

An ActivityInstance contains multiple WorkflowSteps.

WorkflowSteps execute the ActivityInstance.

---

### Database Constraint

UNIQUE(project_id, wbs_item_id, location_id)

Ensures one ActivityInstance per WBS item and location within a project.

---

## Core Attributes

id

name

code

project_id

wbs_item_id

location_id

planned_start

planned_finish

planned_duration

status  
Status Allowed Values

- ACTIVE

- COMPLETED

- CANCELLED

READY is not a status.

Ready is a computed condition.

created_at

updated_at

---

## Owned Concepts

ActivityInstance owns:

- construction scope
- location assignment
- planning commitment
- aggregated progress
- aggregated planned cost

---

## Does Not Own

ActivityInstance does not own:

- execution
- inspections
- approvals
- blockers
- work orders
- daily reports
- BOQ items

These belong to other runtime entities.

---

## Progress Responsibility

ActivityInstance does not create progress.

WorkflowSteps create progress.

ActivityInstance aggregates WorkflowStep progress.

---

## Cost Responsibility

ActivityInstance does not calculate costs directly.

WorkflowSteps own BOQ mappings.

ActivityInstance aggregates planned costs from WorkflowSteps.

---

## Notes

ActivityInstance is the bridge between Planning and Runtime.

Construction Reality

↓

ActivityInstance

↓

Execution Reality

↓

WorkflowStep

ActivityInstance is the primary construction scope entity inside BetavanX.

---

# WorkflowStep

## Purpose

Represents a measurable execution stage required to complete an ActivityInstance.

WorkflowStep is the primary execution entity of BetavanX.

WorkflowStep is where construction execution becomes operational reality.

---

## Layer

Execution Reality

---

## Owner

Runtime Core

---

## Definition

WorkflowStep

=

Execution Reality

WorkflowSteps represent the actual execution stages performed in the field.

Examples:

- Rebar
- Formwork
- Concrete
- Masonry
- Waterproofing

---

## Creation Source

WorkflowSteps are automatically created from WorkflowStepTemplates.

WorkflowStepTemplate

↓

Snapshot

↓

WorkflowStep

WorkflowSteps preserve historical execution knowledge.

Template updates do not affect existing WorkflowSteps.

---

## Lifecycle

Planned

↓

In Progress

↓

Completed

↓

Inspection Pending

↓

Approved

---

### Failure Path

Inspection Failed

↓

Rework Required

↓

In Progress

---

## Status Allowed Values

- PLANNED
- IN_PROGRESS
- COMPLETED
- INSPECTION_PENDING
- INSPECTION_FAILED
- REWORK_REQUIRED
- APPROVED

READY is not a status.

READY is a computed condition represented by `ready BOOLEAN`.

## Core Relationships

### ActivityInstance

N:1

A WorkflowStep belongs to one ActivityInstance.

---

### WorkflowStepTemplate

N:1

A WorkflowStep originates from a WorkflowStepTemplate snapshot.

---

### WorkOrder

N:N

A WorkflowStep may be executed through multiple WorkOrders.

A WorkOrder may contain multiple WorkflowSteps.

Relationship implemented through:

work_order_workflow_steps

Junction constraint:

UNIQUE(work_order_id, workflow_step_id)

Examples:

WorkflowStep

Rebar @ Column C5

↓

WO-01

WO-02

WO-03

---

WorkOrder

WO-2026-06-10

↓

Rebar @ C5

Rebar @ C6

Masonry @ W12

This relationship enables flexible execution planning while preserving WorkflowStep ownership of progress.

---

### DailyReport

1:N (Indirect through WorkOrders)

DailyReports provide execution evidence.

---

### Inspection

1:N

A WorkflowStep may have multiple inspections.

---

### Approval

1:N

A WorkflowStep may have multiple approvals.

Phase 1 typically uses a single final approval.

---

### Blocker

1:N

A WorkflowStep may contain multiple blockers.

---

### BOQMapping

1:N

A WorkflowStep may be linked to multiple BOQ mappings.

Junction constraint:

UNIQUE(workflow_step_id, boq_item_id)

---

## Core Attributes

id

activity_instance_id

workflow_template_id

name

code

description

status

planned_start

planned_finish

planned_duration

actual_start

actual_finish

created_at

updated_at

---

## Progress Attributes

progress_percent

planned_weight

earned_value

earned_value is a derived field.

earned_value is not persisted.

earned_value = Workflow Progress × Planned Cost

---

## Execution Attributes

ready

ready_reason

execution_notes

---

## Ownership

WorkflowStep owns:

- execution state
- progress
- inspections
- approvals
- blockers
- work orders
- assigned resources
- assigned crews
- assigned contractors
- assigned supervisors
- BOQ mappings

---

## Does Not Own

WorkflowStep does not own:

- project scope
- location hierarchy
- planning structure
- financial measurement definitions

---

## Progress Responsibility

WorkflowStep owns progress.

Workflow Progress is calculated from completed WorkOrder Weights.

Formula:

Workflow Progress

=

Σ Completed WorkOrder Weights

/

Total Workflow Weight

---

## Approval Responsibility

WorkflowStep owns execution acceptance.

Progress and Approval are independent.

Example:

Progress = 100%

Status = Approval Pending

This is valid.

---

## Inspection Responsibility

WorkflowStep owns quality verification.

Workflow execution may be complete while inspection remains pending.

Inspection determines quality acceptance.

---

## Ready Responsibility

Ready is a computed condition.

Ready

≠

Status

Ready

=

Computed Condition

---

## Ready Evaluation Inputs

Ready may depend on:

- required drawings available
- required permits available
- required approvals completed
- required materials available
- required resources assigned
- required documents available
- predecessor workflow approved

---

## Blocker Responsibility

Blocked

≠

Not Ready

Not Ready

=

Required conditions missing

Blocked

=

Unexpected operational interruption

Examples:

- weather
- equipment failure
- labor shortage
- access restriction
- material delivery failure

---

## Resource Responsibility

WorkflowStep owns resource assignments.

Examples:

- manpower
- crews
- equipment
- contractors
- supervisors

Resource ownership belongs to WorkflowStep.

Not WorkOrder.

---

## BOQ Responsibility

WorkflowStep owns BOQ mappings.

WorkflowStep

↓

BOQMapping

↓

BOQItem

WorkflowStep does not own BOQItems directly.

---

## Cost Responsibility

WorkflowStep owns planned cost relationships.

WorkflowStep Planned Cost

=

Sum of BOQ Mapping Values

ActivityInstances aggregate WorkflowStep costs.

---

## Execution Knowledge

WorkflowStep inherits execution knowledge from WorkflowStepTemplate snapshots.

Examples:

- method statement
- safety requirements
- inspection checklist
- required resources
- execution guide
- standard references
- permit requirements
- typical drawings

---

## Document Requirements

WorkflowStep may require:

- drawings
- permits
- approvals
- technical documents
- method statements
- safety instructions

---

## Future BIM Integration

Future versions may connect WorkflowSteps to:

- BIM Elements
- Revit Objects
- Model Quantities

This is outside Phase 1 scope.

---

## Strategic Position

Construction Reality

↓

ActivityInstance

↓

Execution Reality

↓

WorkflowStep

↓

Execution Coordination

↓

WorkOrder

↓

Execution Evidence

↓

DailyReport

WorkflowStep is the center of operational execution inside BetavanX.

---

## Notes

If ActivityInstance is the digital identity of construction scope,

WorkflowStep is the digital identity of construction execution.

WorkflowStep is the most important runtime entity in BetavanX.

---

# BOQItem

## Purpose

Represents a financial measurement item within a project.

BOQItems define quantities, units, rates, and planned values used for financial measurement.

BOQItem is the primary financial measurement entity of BetavanX.

---

## Layer

Financial Measurement Reality

---

## Owner

Planning Layer

---

## Definition

BOQItem

=

Bill Of Quantity Item

A BOQItem defines a measurable unit of work together with its commercial value.

---

## Examples

- Rebar Installation
- Concrete Placement
- Formwork Installation
- Masonry Work
- Waterproofing

---

## Lifecycle

Draft

↓

Approved

↓

Active

↓

Closed

---

## Core Relationships

### Project

N:1

A BOQItem belongs to a single Project.

---

### BOQMapping

1:N

A BOQItem may be linked to multiple BOQMappings.

---

## Core Attributes

id

project_id

item_code

item_number

title

description

unit

quantity

rate

planned_cost

status

created_at

updated_at

---

## Financial Attributes

quantity

unit

rate

planned_cost

currency

---

## Ownership

BOQItem owns:

- measurement units
- planned quantities
- rates
- planned values
- valuation rules

---

## Does Not Own

BOQItem does not own:

- execution
- inspections
- approvals
- blockers
- resources
- work orders

---

## Cost Responsibility

Planned Cost

=

Quantity × Rate

BOQItems define planned financial value.

---

## Progress Responsibility

BOQItems do not create progress.

WorkflowSteps create progress.

BOQItems use progress for valuation purposes.

---

## Earned Value Responsibility

Earned Value

=

Workflow Progress × Planned Cost

BOQItems provide the planned value component.

---

## Strategic Position

Construction Reality

↓

ActivityInstance

---

Execution Reality

↓

WorkflowStep

---

Financial Reality

↓

BOQItem

---

## Notes

BOQItems represent financial measurement reality.

They are intentionally separated from execution reality.

This separation enables future cost intelligence and earned value analysis

---

# BOQMapping

## Purpose

Connect WorkflowSteps to BOQItems.

BOQMapping is the bridge between execution reality and financial measurement reality.

---

## Layer

Financial Integration Layer

---

## Owner

Runtime Support Layer

---

## Definition

BOQMapping

=

Execution-to-Financial Link

WorkflowStep

↓

BOQMapping

↓

BOQItem

---

## Lifecycle

Created

↓

Active

↓

Closed

---

## Core Relationships

### WorkflowStep

N:1

A BOQMapping belongs to one WorkflowStep.

---

### BOQItem

N:1

A BOQMapping belongs to one BOQItem.

---

## Core Attributes

id

workflow_step_id

boq_item_id

allocated_quantity

allocated_cost

notes

created_at

updated_at

---

## Ownership

BOQMapping owns:

- quantity allocation
- cost allocation
- valuation linkage

---

## Does Not Own

BOQMapping does not own:

- execution
- progress
- inspections
- approvals
- resources

---

## Quantity Allocation

Examples:

BOQ Item

Rebar Installation

1000 kg

↓

WorkflowStep

Rebar @ Column C5

100 kg

---

WorkflowStep

Rebar @ Column C6

120 kg

---

WorkflowStep

Rebar @ Column C7

80 kg

---

BOQMapping stores these allocations.

---

## Cost Allocation

Allocated Cost

=

Allocated Quantity × BOQ Rate

BOQMapping enables WorkflowStep planned cost calculation.

---

## Cost Responsibility

WorkflowStep Planned Cost

=

Sum of BOQMapping Allocated Costs

---

## Strategic Position

Execution Reality

↓

WorkflowStep

↓

BOQMapping

↓

BOQItem

↓

Financial Measurement Reality

---

## Notes

BOQMapping is an associative entity.

BOQMapping is not Runtime Core.

BOQMapping exists to connect execution reality and financial reality while keeping both domains independent.

This separation is a foundational architectural principle of BetavanX.

---

# WorkOrder

## Purpose

Represents an execution commitment package derived from one or more WorkflowSteps.

WorkOrders coordinate daily field execution.

WorkOrders are execution coordination entities.

WorkOrders are not operational truth.

---

## Layer

Execution Coordination

---

## Owner

Runtime Core

---

## Definition

WorkOrder

=

Execution Slice

A WorkOrder represents a package of work intended to be executed by a specific team during a specific time period.

---

## Examples

Daily Work Order

2026-06-10

Includes:

- Rebar @ C5
- Rebar @ C6
- Rebar @ C7
- Masonry @ W12

---

## Lifecycle

Created

↓

Assigned

↓

In Progress

↓

Completed

or

Cancelled

---

## Core Relationships

### WorkflowStep

N:N

A WorkOrder may contain multiple WorkflowSteps.

A WorkflowStep may generate multiple WorkOrders.

---

### DailyReport

1:N

A WorkOrder may have multiple DailyReports.

---

## Core Attributes

id

project_id

work_order_number

title

description

planned_date

status

created_by

Phase 1 stores user UUID reference only.

No users table exists in Phase 1.

No foreign key enforcement is applied.

Future versions may introduce a users table.

created_at

updated_at

---

## Ownership

WorkOrder owns:

- execution commitment
- daily coordination package
- execution assignment scope

---

## Does Not Own

WorkOrder does not own:

- progress
- inspections
- approvals
- blockers
- resources
- costs

These belong to WorkflowSteps.

---

## Progress Responsibility

WorkOrders contribute to progress.

WorkOrders do not own progress.

WorkflowSteps own progress.

---

## Resource Responsibility

Resources are assigned to WorkflowSteps.

WorkOrders display assigned execution responsibilities.

Resource ownership remains with WorkflowSteps.

---

## Cost Responsibility

WorkOrders do not own costs.

WorkflowSteps own BOQ mappings and planned costs.

---

## Execution Responsibility

WorkOrders coordinate execution.

They do not define execution logic.

Execution logic belongs to WorkflowSteps.

---

## Strategic Position

Construction Reality

↓

ActivityInstance

↓

Execution Reality

↓

WorkflowStep

↓

Execution Coordination

↓

WorkOrder

↓

Execution Evidence

↓

DailyReport

---

## Notes

WorkOrder is intentionally lightweight.

WorkOrder exists to coordinate execution.

WorkOrder is not the center of the runtime model.

WorkflowStep remains the primary operational entity.

---

# DailyReport

## Purpose

Represents execution evidence produced during field operations.

DailyReports document what actually happened during execution.

DailyReport is the primary execution evidence entity of BetavanX.

---

## Layer

Execution Evidence

---

## Owner

Runtime Core

---

## Definition

DailyReport

=

Execution Evidence

A DailyReport records actual execution observations for a specific WorkOrder during a specific reporting period.

---

## Examples

Daily Report

2026-06-10

Work Performed:

- Rebar installation continued
- Formwork preparation completed

Issues:

- Material delivery delayed

Photos:

- Attached

Notes:

- Additional manpower assigned

---

## Lifecycle

Draft

↓

Submitted

↓

Reviewed

↓

Accepted

or

Rejected

---

## Core Relationships

### WorkOrder

N:1

A DailyReport belongs to one WorkOrder.

A WorkOrder may have multiple DailyReports.

---

### WorkflowStep

N:N (Indirect)

DailyReports contribute execution evidence to WorkflowSteps through WorkOrders.

---

## Core Attributes

id

work_order_id

report_date

status

summary

execution_notes

delay_notes

issue_notes

weather_notes

submitted_by

Phase 1 stores user UUID reference only.

No users table exists in Phase 1.

No foreign key enforcement is applied.

Future versions may introduce a users table.

submitted_at

created_at

updated_at

---

## Evidence Attributes

evidence_metadata (JSONB)

Stores:

- photos
- attachments
- documents
- observations

---

## Resource Reporting Attributes

reported_manpower

reported_equipment

reported_materials

resource_notes

---

## Ownership

DailyReport owns:

- execution observations
- field evidence
- execution notes
- issue reporting
- delay reporting
- attached photos
- attached documents

---

## Does Not Own

DailyReport does not own:

- progress
- approvals
- inspections
- costs
- execution logic

These belong to WorkflowSteps.

---

## Progress Responsibility

DailyReports do not own progress.

DailyReports provide evidence that supports progress updates.

WorkflowSteps remain the owners of progress.

---

## Inspection Responsibility

DailyReports do not approve work.

DailyReports provide evidence that may later support inspections.

---

## Approval Responsibility

DailyReports do not approve execution.

Approvals remain independent workflow decisions.

---

## Cost Responsibility

Phase 1 DailyReports do not calculate actual cost.

Future versions may use DailyReports as inputs for:

- labor cost analysis
- equipment utilization
- material consumption
- productivity measurement

---

## Learning Responsibility

DailyReports are a primary source of organizational learning.

Future analysis may identify:

- recurring blockers
- productivity patterns
- quality issues
- execution improvements

---

## Strategic Position

Construction Reality

↓

ActivityInstance

↓

Execution Reality

↓

WorkflowStep

↓

Execution Coordination

↓

WorkOrder

↓

Execution Evidence

↓

DailyReport

---

## Notes

DailyReports represent observed reality.

DailyReports are not planning documents.

DailyReports are not approval documents.

DailyReports are the historical memory of project execution.

Over time DailyReports become one of the most valuable data assets inside BetavanX.

---

# Inspection

## Purpose

Represents a formal quality verification activity performed on a WorkflowStep.

Inspections determine whether completed work satisfies defined quality requirements.

Inspection is the primary quality verification entity of BetavanX.

---

## Layer

Quality Verification

---

## Owner

Runtime Core

---

## Definition

Inspection

=

Quality Verification

An Inspection evaluates execution quality against predefined acceptance criteria.

Inspection does not perform work.

Inspection verifies work.

---

## Examples

- Rebar Inspection
- Formwork Inspection
- Concrete Inspection
- Waterproofing Inspection
- Masonry Inspection

---

## Lifecycle

Created

↓

Scheduled

↓

In Progress

↓

Passed

or

Failed

---

### Failure Path

Failed

↓

Punch Items Created

↓

Rework Required

↓

New Inspection

---

## Core Relationships

### WorkflowStep

N:1

An Inspection belongs to a single WorkflowStep.

A WorkflowStep may have multiple Inspections.

---

### PunchItem

1:N

An Inspection may generate multiple PunchItems.

---

### Approval

0:N

Successful inspections may support approvals.

Approval remains a separate entity.

---

## Core Attributes

id

workflow_step_id

inspection_type

inspection_date

status

inspector_name

inspection_notes

result

created_at

updated_at

---

## Evidence Attributes

photos

attachments

inspection_documents

checklist_results

observations

---

## Ownership

Inspection owns:

- quality verification
- inspection findings
- inspection evidence
- checklist results
- inspection outcome

---

## Does Not Own

Inspection does not own:

- execution
- progress
- approvals
- costs
- resources

These belong to other runtime entities.

---

## Quality Responsibility

Inspection determines whether execution quality satisfies required standards.

Inspection validates quality.

Inspection does not validate planning.

---

## Progress Responsibility

Inspection does not create progress.

Inspection does not modify progress.

WorkflowSteps own progress.

---

## Approval Responsibility

Inspection and Approval are separate concepts.

Example:

Workflow Progress = 100%

Inspection = Passed

Approval = Pending

This is a valid state.

---

## Failure Responsibility

Failed inspections create quality findings.

These findings are recorded as PunchItems.

Inspection

↓

PunchItem

↓

Rework

↓

Reinspection

---

## Checklist Responsibility

Inspection may use:

- inspection checklists
- acceptance criteria
- standards
- technical requirements

These are typically inherited from WorkflowStepTemplate knowledge.

---

## Strategic Position

Construction Reality

↓

ActivityInstance

↓

Execution Reality

↓

WorkflowStep

↓

Quality Verification

↓

Inspection

↓

Quality Findings

↓

PunchItem

---

## Notes

Inspection represents quality truth.

Inspection answers:

"Was the work executed correctly?"

Inspection does not answer:

"Was the work completed?"

Completion belongs to WorkflowStep.

Acceptance belongs to Approval.

Quality verification belongs to Inspection.

This separation is a foundational principle of the BetavanX Runtime Core.

---

# PunchItem

## Purpose

Represents a quality deficiency, non-conformance, or corrective action identified during an Inspection.

PunchItems track issues that must be resolved before final acceptance.

PunchItem is the primary quality finding entity of BetavanX.

---

## Layer

Quality Findings

---

## Owner

Runtime Core

---

## Definition

PunchItem

=

Quality Deficiency

A PunchItem represents a specific issue discovered during quality verification that requires corrective action.

---

## Examples

- Missing Rebar Cover
- Incorrect Rebar Spacing
- Honeycombing in Concrete
- Formwork Alignment Issue
- Waterproofing Defect
- Missing Safety Protection

---

## Lifecycle

Open

↓

Assigned

↓

In Progress

↓

Resolved

↓

Verified

↓

Closed

---

### Rejection Path

Verified

↓

Rejected

↓

Reopened

↓

In Progress

---

## Core Relationships

### Inspection

N:1

A PunchItem originates from a single Inspection.

An Inspection may generate multiple PunchItems.

---

### WorkflowStep

N:1

A PunchItem belongs to a WorkflowStep.

A WorkflowStep may contain multiple PunchItems.

---

## Core Attributes

id

workflow_step_id

inspection_id

title

description

severity

status

location_reference

assigned_to

Phase 1 stores user UUID reference only.

No users table exists in Phase 1.

No foreign key enforcement is applied.

Future versions may introduce a users table.

due_date

resolution_notes

created_at

updated_at

closed_at

---

## Evidence Attributes

photos

attachments

verification_photos

verification_notes

---

## Ownership

PunchItem owns:

- quality deficiencies
- corrective actions
- issue resolution tracking
- verification history

---

## Does Not Own

PunchItem does not own:

- execution progress
- approvals
- inspections
- costs
- planning commitments

These belong to other entities.

---

## Severity Levels

Examples:

Low

Medium

High

Critical

Severity classification helps prioritize corrective actions.

---

## Resolution Responsibility

PunchItems require corrective action.

Correction occurs through execution activities.

Verification occurs through inspection.

---

## Verification Responsibility

Resolving a PunchItem does not automatically close it.

A PunchItem must be verified before closure.

Example:

Issue Fixed

↓

Verification Inspection

↓

Closed

---

## Progress Responsibility

PunchItems do not own progress.

However unresolved PunchItems may prevent final acceptance.

Example:

Workflow Progress = 100%

PunchItems = Open

↓

Approval = Blocked

---

## Approval Responsibility

Open PunchItems may prevent approval.

Approval decisions may depend on PunchItem status.

Approval ownership remains with Approval entities.

---

## Rework Relationship

PunchItems may trigger:

Rework Required

↓

Execution

↓

Inspection

↓

Verification

↓

Closure

---

## Strategic Position

Construction Reality

↓

ActivityInstance

↓

Execution Reality

↓

WorkflowStep

↓

Quality Verification

↓

Inspection

↓

Quality Finding

↓

PunchItem

↓

Corrective Action

↓

Verification

---

## Notes

PunchItems represent discovered quality problems.

PunchItems are not execution work.

PunchItems are not inspections.

PunchItems are not approvals.

PunchItems exist to ensure that quality issues are visible, traceable, and verifiable until closure.

Over time PunchItem data becomes a valuable source of quality intelligence and organizational learning.

---

# Approval

## Purpose

Represents formal acceptance of a WorkflowStep after successful execution and quality verification.

Approval confirms that work is accepted for progression, handover, or closure.

Approval is the primary acceptance entity of BetavanX.

---

## Layer

Operational Approval

---

## Owner

Runtime Core

---

## Definition

Approval

=

Formal Acceptance

Approval represents an authorization decision confirming that a WorkflowStep satisfies all required acceptance conditions.

Approval does not perform work.

Approval does not inspect work.

Approval accepts work.

---

## Examples

- Rebar Approved
- Formwork Approved
- Concrete Approved
- Waterproofing Approved
- Masonry Approved

---

## Lifecycle

Pending

↓

Under Review

↓

Approved

or

Rejected

---

### Rejection Path

Rejected

↓

Rework Required

↓

Inspection

↓

Approval Review

---

## Core Relationships

### WorkflowStep

N:1

An Approval belongs to a single WorkflowStep.

A WorkflowStep may have multiple Approvals over time.

---

### Inspection

N:N (Logical Relationship)

Approvals may depend on successful inspections.

Inspections remain independent entities.

---

### PunchItem

N:N (Logical Relationship)

Open PunchItems may prevent approval.

Approval depends on Inspection and PunchItem outcomes.

Approval does not maintain direct foreign key relationships with Inspection or PunchItem.

Approval dependencies are enforced at application level.

---

## Core Attributes

id

workflow_step_id

approval_type

status

approval_date

approved_by

Phase 1 stores user UUID reference only.

No users table exists in Phase 1.

No foreign key enforcement is applied.

Future versions may introduce a users table.

approval_notes

rejection_reason

created_at

updated_at

---

## Ownership

Approval owns:

- acceptance decisions
- approval history
- approval evidence
- approval outcomes

---

## Does Not Own

Approval does not own:

- execution
- progress
- inspections
- quality findings
- costs
- resources

These belong to other entities.

---

## Approval Responsibility

Approval determines whether execution can be formally accepted.

Approval answers:

"Can this work be accepted?"

Approval does not answer:

"Was this work completed?"

Completion belongs to WorkflowStep.

---

## Progress Responsibility

Approval does not own progress.

Progress and Approval are independent concepts.

Example:

Workflow Progress = 100%

Approval Status = Pending

This is valid.

---

## Inspection Dependency

Approval may depend on:

- successful inspections
- completed checklists
- quality verification

Phase 1 uses simplified approval logic.

---

## PunchItem Dependency

Approval may require:

Open Punch Items = 0

before approval can be granted.

Future versions may support configurable approval rules.

---

## Phase 1 Simplification

Phase 1 uses a simplified final approval model.

Typical flow:

Completed

↓

Inspection Passed

↓

Approval Granted

Future versions may support:

- Client Approval
- Consultant Approval
- Survey Approval
- Authority Approval
- Multi-Stage Approval

---

## Strategic Position

Construction Reality

↓

ActivityInstance

↓

Execution Reality

↓

WorkflowStep

↓

Quality Verification

↓

Inspection

↓

Quality Findings

↓

PunchItem

↓

Operational Approval

↓

Approval

---

## Notes

Approval represents acceptance truth.

Inspection verifies quality.

Approval grants acceptance.

Execution, quality verification, and acceptance are intentionally separated in BetavanX.

This separation improves accountability, auditability, and future scalability.  
  
Approval dependencies are enforced at application level.

Approval does not maintain direct foreign key relationships with Inspection or PunchItem.

Inspection and PunchItem requirements are validated by business rules before approval can be granted.

---

# Blocker

## Purpose

Represents an unexpected operational condition that prevents execution of a WorkflowStep despite planning readiness.

Blockers provide visibility into execution interruptions and operational constraints.

Blocker is the primary operational constraint entity of BetavanX.

---

## Layer

Operational Constraints

---

## Owner

Runtime Core

---

## Definition

Blocker

=

Unexpected Operational Constraint

A Blocker represents a condition that prevents execution from continuing even though the WorkflowStep is otherwise ready for execution.

---

## Core Principle

Blocked

≠

Not Ready

---

Not Ready

=

Required execution conditions are missing.

Examples:

- missing permit
- missing drawing
- missing approval
- missing material assignment
- missing resource assignment

---

Blocked

=

Unexpected operational interruption.

Examples:

- weather
- equipment breakdown
- labor shortage
- site access restriction
- utility conflict
- stop work order
- material delivery failure
- safety incident

---

## Examples

- Concrete Delivery Delayed
- Crane Breakdown
- Excavation Permit Suspension
- Labor Strike
- Heavy Rainfall
- Site Access Closed
- Utility Relocation Delay

---

## Lifecycle

Open

↓

Acknowledged

↓

Mitigation In Progress

↓

Resolved

↓

Closed

---

### Reopen Path

Closed

↓

Reopened

↓

Mitigation In Progress

---

## Core Relationships

### WorkflowStep

N:1

A Blocker belongs to a single WorkflowStep.

A WorkflowStep may contain multiple Blockers.

---

### DailyReport

N:N (Logical Relationship)

DailyReports may record blocker observations.

Blockers remain independent entities.

---

## Core Attributes

id

workflow_step_id

title

description

blocker_type

severity

status

detected_date

resolved_date

reported_by

Phase 1 stores user UUID reference only.

No users table exists in Phase 1.

No foreign key enforcement is applied.

Future versions may introduce a users table.

resolution_notes

created_at

updated_at

---

## Classification Attributes

blocker_category

root_cause

impact_level

responsible_party

---

## Ownership

Blocker owns:

- operational interruptions
- execution constraints
- blocker history
- mitigation records
- resolution tracking

---

## Does Not Own

Blocker does not own:

- execution progress
- approvals
- inspections
- quality findings
- costs

These belong to other entities.

---

## Execution Responsibility

Blockers may prevent execution.

Blockers do not modify execution logic.

Execution logic remains owned by WorkflowStep.

---

## Progress Responsibility

Blockers do not own progress.

However Blockers may indirectly delay progress.

Example:

Workflow Progress = 40%

Blocker = Open

↓

Execution Paused

↓

Progress Growth Delayed

---

## Approval Responsibility

Blockers do not own approvals.

However unresolved blockers may delay completion and therefore postpone approval.

---

## Mitigation Responsibility

Blockers should be actively managed.

Typical flow:

Blocker Detected

↓

Root Cause Identified

↓

Mitigation Planned

↓

Mitigation Executed

↓

Resolved

---

## Classification Examples

### Weather

- rain
- snow
- high wind
- extreme temperature

---

### Equipment

- equipment breakdown
- unavailable equipment
- maintenance issue

---

### Material

- delivery delay
- shortage
- quality issue

---

### Workforce

- labor shortage
- absenteeism
- strike

---

### Site Conditions

- access restriction
- utility conflict
- unforeseen conditions

---

### External

- authority order
- regulatory restriction
- client hold

---

## Learning Responsibility

Blockers are a primary source of operational learning.

Future analysis may identify:

- recurring constraints
- project risks
- planning weaknesses
- contractor performance issues

---

## Strategic Position

Construction Reality

↓

ActivityInstance

↓

Execution Reality

↓

WorkflowStep

↓

Operational Constraint

↓

Blocker

↓

Mitigation

↓

Resolution

---

## Notes

Blockers represent operational reality.

A WorkflowStep may be:

Ready = True

and

Blocked = True

at the same time.

This is valid.

Example:

All requirements satisfied

↓

Ready = True

↓

Crane Breakdown

↓

Blocked = True

The distinction between Ready and Blocked is a foundational architectural principle of BetavanX.

Blockers make execution interruptions visible, measurable, and traceable.