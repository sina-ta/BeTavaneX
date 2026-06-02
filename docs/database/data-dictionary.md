# Data Dictionary

Status: Draft

Version: 1.0

Purpose:

Define the database fields, constraints, ownership rules, and implementation requirements for BetavanX entities.

This document serves as the source of truth for:

- PostgreSQL Schema
- Backend Models
- API Contracts
- Frontend Forms

---

# ActivityInstance

## Table

activity_instances

---

## Primary Key

id

Type:

UUID

Nullable:

No

Description:

Unique identifier.

---

## project_id

Type:

UUID

Nullable:

No

FK:

[projects.id](http://projects.id)

Description:

Parent project.

---

## wbs_item_id

Type:

UUID

Nullable:

No

FK:

wbs_[items.id](http://items.id)

Description:

Source WBS item.

---

## location_id

Type:

UUID

Nullable:

No

FK:

[locations.id](http://locations.id)

Description:

Assigned location.

---

## code

Type:

VARCHAR(100)

Nullable:

No

Unique:

Yes

Description:

Human-readable identifier.

Example:

COLUMN-C5

---

## name

Type:

VARCHAR(255)

Nullable:

No

Description:

Display name.

Example:

Column C5

---

## planned_start

Type:

DATE

Nullable:

Yes

---

## planned_finish

Type:

DATE

Nullable:

Yes

---

## planned_duration_days

Type:

INTEGER

Nullable:

Yes

---

## status

Type:

VARCHAR(50)

Nullable:

No

Default:

ACTIVE

Allowed Values:

- ACTIVE
- COMPLETED
- CANCELLED

---

## created_at

Type:

TIMESTAMP

Nullable:

No

---

## updated_at

Type:

TIMESTAMP

Nullable:

No

---

# Constraints

UNIQUE(project_id, code)

---

UNIQUE(project_id, wbs_item_id, location_id)

---

# WorkflowStep

## Table

workflow_steps

---

## Primary Key

id

Type:

UUID

Nullable:

No

---

## activity_instance_id

Type:

UUID

Nullable:

No

FK:

activity_[instances.id](http://instances.id)

---

## workflow_template_id

Type:

UUID

Nullable:

Yes

FK:

workflow_step_[templates.id](http://templates.id)

---

## code

Type:

VARCHAR(100)

Nullable:

No

---

## name

Type:

VARCHAR(255)

Nullable:

No

Example:

Rebar

---

## status

Type:

VARCHAR(50)

Nullable:

No

Allowed Values:

- PLANNED
- IN_PROGRESS
- COMPLETED
- INSPECTION_PENDING
- INSPECTION_FAILED
- REWORK_REQUIRED
- APPROVED

---

## ready

Type:

BOOLEAN

Nullable:

No

Default:

FALSE

---

## progress_percent

Type:

NUMERIC(5,2)

Nullable:

No

Default:

0

Range:

0-100

---

## earned_value

Derived Field

Not Persisted

Calculated as:

Workflow Progress × Planned Cost

---

## planned_weight

Type:

NUMERIC(8,2)

Nullable:

Yes

Description:

Weight used for ActivityInstance progress rollup.

---

## planned_start

Type:

DATE

Nullable:

Yes

---

## planned_finish

Type:

DATE

Nullable:

Yes

---

## actual_start

Type:

DATE

Nullable:

Yes

---

## actual_finish

Type:

DATE

Nullable:

Yes

---

## created_at

Type:

TIMESTAMP

Nullable:

No

---

## updated_at

Type:

TIMESTAMP

Nullable:

No

---

# BOQItem

## Table

boq_items

---

## Primary Key

id

Type:

UUID

Nullable:

No

Description:

Unique identifier.

---

## project_id

Type:

UUID

Nullable:

No

FK:

[projects.id](http://projects.id)

Description:

Parent project.

---

## item_number

Type:

VARCHAR(100)

Nullable:

No

Description:

BOQ reference number.

Example:

03-01-002

---

## item_code

Type:

VARCHAR(100)

Nullable:

Yes

Description:

Internal BOQ code.

---

## title

Type:

VARCHAR(255)

Nullable:

No

Description:

BOQ item title.

Example:

Rebar Installation

---

## description

Type:

TEXT

Nullable:

Yes

Description:

Detailed BOQ description.

---

## unit

Type:

VARCHAR(50)

Nullable:

No

Examples:

kg

m²

m³

m

nos

---

## quantity

Type:

NUMERIC(18,3)

Nullable:

No

Description:

Planned BOQ quantity.

---

## rate

Type:

NUMERIC(18,2)

Nullable:

No

Description:

Unit rate.

---

## planned_cost

Type:

NUMERIC(18,2)

Nullable:

No

Description:

Quantity × Rate

---

## currency

Type:

VARCHAR(10)

Nullable:

No

Default:

IRR

---

## status

Type:

VARCHAR(50)

Nullable:

No

Default:

ACTIVE

Allowed Values:

- DRAFT
- APPROVED
- ACTIVE
- CLOSED

---

## created_at

Type:

TIMESTAMP

Nullable:

No

---

## updated_at

Type:

TIMESTAMP

Nullable:

No

---

# Constraints

planned_cost

=

quantity × rate

---

quantity > 0

---

rate >= 0

---

# BOQMapping

## Table

boq_mappings

---

## Primary Key

id

Type:

UUID

Nullable:

No

---

## workflow_step_id

Type:

UUID

Nullable:

No

FK:

workflow_[steps.id](http://steps.id)

Description:

Execution owner.

---

## boq_item_id

Type:

UUID

Nullable:

No

FK:

boq_[items.id](http://items.id)

Description:

Financial owner.

---

## allocated_quantity

Type:

NUMERIC(18,3)

Nullable:

No

Description:

Quantity allocated to the WorkflowStep.

---

## allocated_cost

Type:

NUMERIC(18,2)

Nullable:

No

Description:

Financial value allocated to the WorkflowStep.

---

## allocation_percentage

Type:

NUMERIC(6,2)

Nullable:

Yes

Description:

Percentage of BOQ quantity allocated.

Range:

0 - 100

---

## notes

Type:

TEXT

Nullable:

Yes

Description:

Allocation explanation.

---

## created_at

Type:

TIMESTAMP

Nullable:

No

---

## updated_at

Type:

TIMESTAMP

Nullable:

No

---

# Constraints

allocated_quantity > 0

---

allocated_cost >= 0

---

allocated_cost

=

allocated_quantity × BOQItem.rate

---

A BOQItem may have multiple BOQMappings.

---

A WorkflowStep may have multiple BOQMappings.

---

UNIQUE(workflow_step_id, boq_item_id)

---

# WorkOrder

## Table

work_orders

---

## Primary Key

id

Type:

UUID

Nullable:

No

---

## project_id

Type:

UUID

Nullable:

No

FK:

[projects.id](http://projects.id)

---

## work_order_number

Type:

VARCHAR(100)

Nullable:

No

Unique:

Yes

Description:

Human-readable WorkOrder number.

Example:

WO-2026-00125

---

## title

Type:

VARCHAR(255)

Nullable:

No

Description:

WorkOrder title.

---

## description

Type:

TEXT

Nullable:

Yes

---

## planned_date

Type:

DATE

Nullable:

No

Description:

Planned execution date.

---

## status

Type:

VARCHAR(50)

Nullable:

No

Default:

CREATED

Allowed Values:

- CREATED
- ASSIGNED
- IN_PROGRESS
- COMPLETED
- CANCELLED

---

## created_by

Type:

UUID

Nullable:

Yes

Description:

User who created the WorkOrder.

Phase 1 stores user UUID reference only.

No users table exists in Phase 1.

No foreign key enforcement is applied.

Future versions may introduce a users table.

---

## created_at

Type:

TIMESTAMP

Nullable:

No

---

## updated_at

Type:

TIMESTAMP

Nullable:

No

---

# Constraints

work_order_number must be unique.

---

planned_date is required.

---

UNIQUE(project_id, work_order_number)

---

# WorkOrder WorkflowStep Mapping

## Table

work_order_workflow_steps

Purpose:

Many-to-many relationship between WorkOrders and WorkflowSteps.

---

## id

Type:

UUID

Nullable:

No

---

## work_order_id

Type:

UUID

Nullable:

No

FK:

work_[orders.id](http://orders.id)

---

## workflow_step_id

Type:

UUID

Nullable:

No

FK:

workflow_[steps.id](http://steps.id)

---

## execution_weight

Type:

NUMERIC(8,2)

Nullable:

No

Description:

Contribution of this WorkOrder toward WorkflowStep completion.

Example:

33.33

---

## created_at

Type:

TIMESTAMP

Nullable:

No

---

# Constraints

execution_weight > 0

---

UNIQUE(work_order_id, workflow_step_id)

---

WorkflowStep progress is derived from completed WorkOrder weights.

---

# DailyReport

## Table

daily_reports

---

## Primary Key

id

Type:

UUID

Nullable:

No

---

## work_order_id

Type:

UUID

Nullable:

No

FK:

work_[orders.id](http://orders.id)

---

## report_date

Type:

DATE

Nullable:

No

---

## status

Type:

VARCHAR(50)

Nullable:

No

Default:

DRAFT

Allowed Values:

- DRAFT
- SUBMITTED
- REVIEWED
- ACCEPTED
- REJECTED

---

## summary

Type:

TEXT

Nullable:

Yes

Description:

Short execution summary.

---

## execution_notes

Type:

TEXT

Nullable:

Yes

Description:

Work performed.

---

## issue_notes

Type:

TEXT

Nullable:

Yes

Description:

Issues encountered.

---

## delay_notes

Type:

TEXT

Nullable:

Yes

Description:

Delay descriptions.

---

## weather_notes

Type:

TEXT

Nullable:

Yes

Description:

Weather observations.

---

## evidence_metadata

Type:

JSONB

Nullable:

Yes

Description:

Stores photos, attachments, documents, and observations.

---

## submitted_by

Type:

UUID

Nullable:

Yes

Phase 1 stores user UUID reference only.

No users table exists in Phase 1.

No foreign key enforcement is applied.

Future versions may introduce a users table.

---

## submitted_at

Type:

TIMESTAMP

Nullable:

Yes

---

## created_at

Type:

TIMESTAMP

Nullable:

No

---

## updated_at

Type:

TIMESTAMP

Nullable:

No

---

# Resource Reporting Fields

## reported_manpower

Type:

INTEGER

Nullable:

Yes

Default:

0

---

## reported_equipment

Type:

INTEGER

Nullable:

Yes

Default:

0

---

## reported_material_entries

Type:

INTEGER

Nullable:

Yes

Default:

0

---

# Constraints

report_date is required.

---

A WorkOrder may have multiple DailyReports.

---

DailyReports provide execution evidence.

DailyReports do not own progress.

DailyReports do not own approvals.

DailyReports do not own costs.

---

# Inspection

## Table

inspections

---

## Primary Key

id

Type:

UUID

Nullable:

No

---

## workflow_step_id

Type:

UUID

Nullable:

No

FK:

workflow_[steps.id](http://steps.id)

---

## inspection_type

Type:

VARCHAR(100)

Nullable:

No

Examples:

- REBAR
- FORMWORK
- CONCRETE
- WATERPROOFING
- MASONRY

---

## inspection_date

Type:

DATE

Nullable:

No

---

## status

Type:

VARCHAR(50)

Nullable:

No

Allowed Values:

- CREATED
- SCHEDULED
- IN_PROGRESS
- PASSED
- FAILED

---

## inspector_name

Type:

VARCHAR(255)

Nullable:

Yes

---

## inspection_notes

Type:

TEXT

Nullable:

Yes

---

## result

Type:

VARCHAR(50)

Nullable:

No

Allowed Values:

- PASS
- FAIL

---

## created_at

Type:

TIMESTAMP

Nullable:

No

---

## updated_at

Type:

TIMESTAMP

Nullable:

No

---

# Constraints

An Inspection belongs to one WorkflowStep.

A WorkflowStep may have multiple Inspections.

---

# PunchItem

## Table

punch_items

---

## Primary Key

id

Type:

UUID

Nullable:

No

---

## workflow_step_id

Type:

UUID

Nullable:

No

FK:

workflow_[steps.id](http://steps.id)

---

## inspection_id

Type:

UUID

Nullable:

No

FK:

[inspections.id](http://inspections.id)

---

## title

Type:

VARCHAR(255)

Nullable:

No

---

## description

Type:

TEXT

Nullable:

Yes

---

## severity

Type:

VARCHAR(50)

Nullable:

No

Allowed Values:

- LOW
- MEDIUM
- HIGH
- CRITICAL

---

## status

Type:

VARCHAR(50)

Nullable:

No

Allowed Values:

- OPEN
- ASSIGNED
- IN_PROGRESS
- RESOLVED
- VERIFIED
- CLOSED
- REOPENED

---

## assigned_to

Type:

UUID

Nullable:

Yes

Phase 1 stores user UUID reference only.

No users table exists in Phase 1.

No foreign key enforcement is applied.

Future versions may introduce a users table.

---

## due_date

Type:

DATE

Nullable:

Yes

---

## resolution_notes

Type:

TEXT

Nullable:

Yes

---

## closed_at

Type:

TIMESTAMP

Nullable:

Yes

---

## created_at

Type:

TIMESTAMP

Nullable:

No

---

## updated_at

Type:

TIMESTAMP

Nullable:

No

---

# Constraints

A PunchItem must belong to an Inspection.

A PunchItem must belong to a WorkflowStep.

Open PunchItems may block Approval.

---

# Approval

## Table

approvals

---

## Primary Key

id

Type:

UUID

Nullable:

No

---

## workflow_step_id

Type:

UUID

Nullable:

No

FK:

workflow_[steps.id](http://steps.id)

---

## approval_type

Type:

VARCHAR(100)

Nullable:

No

Default:

FINAL

---

## status

Type:

VARCHAR(50)

Nullable:

No

Allowed Values:

- PENDING
- UNDER_REVIEW
- APPROVED
- REJECTED

---

## approval_date

Type:

DATE

Nullable:

Yes

---

## approved_by

Type:

UUID

Nullable:

Yes

Phase 1 stores user UUID reference only.

No users table exists in Phase 1.

No foreign key enforcement is applied.

Future versions may introduce a users table.

---

## approval_notes

Type:

TEXT

Nullable:

Yes

---

## rejection_reason

Type:

TEXT

Nullable:

Yes

---

## created_at

Type:

TIMESTAMP

Nullable:

No

---

## updated_at

Type:

TIMESTAMP

Nullable:

No

---

# Constraints

Approval belongs to a WorkflowStep.

Approval depends on Inspection and PunchItem outcomes.

Approval does not maintain direct foreign key relationships with Inspection or PunchItem.

Approval dependencies are enforced at application level.

Approval does not own progress.

Progress and Approval are independent.

---

# Blocker

## Table

blockers

---

## Primary Key

id

Type:

UUID

Nullable:

No

---

## workflow_step_id

Type:

UUID

Nullable:

No

FK:

workflow_[steps.id](http://steps.id)

---

## title

Type:

VARCHAR(255)

Nullable:

No

---

## description

Type:

TEXT

Nullable:

Yes

---

## blocker_type

Type:

VARCHAR(100)

Nullable:

No

Examples:

- WEATHER
- EQUIPMENT
- MATERIAL
- WORKFORCE
- SITE_CONDITION
- EXTERNAL

---

## severity

Type:

VARCHAR(50)

Nullable:

No

Allowed Values:

- LOW
- MEDIUM
- HIGH
- CRITICAL

---

## status

Type:

VARCHAR(50)

Nullable:

No

Allowed Values:

- OPEN
- ACKNOWLEDGED
- MITIGATION_IN_PROGRESS
- RESOLVED
- CLOSED
- REOPENED

---

## detected_date

Type:

DATE

Nullable:

No

---

## resolved_date

Type:

DATE

Nullable:

Yes

---

## reported_by

Type:

UUID

Nullable:

Yes

Phase 1 stores user UUID reference only.

No users table exists in Phase 1.

No foreign key enforcement is applied.

Future versions may introduce a users table.

---

## root_cause

Type:

TEXT

Nullable:

Yes

---

## resolution_notes

Type:

TEXT

Nullable:

Yes

---

## created_at

Type:

TIMESTAMP

Nullable:

No

---

## updated_at

Type:

TIMESTAMP

Nullable:

No

---

# Constraints

A Blocker belongs to a WorkflowStep.

A WorkflowStep may have multiple Blockers.

Ready = TRUE

and

Blocked = TRUE

is a valid state.

Blockers do not own progress.

Blockers do not own approvals.

---

# Data Dictionary Amendments

Status: Approved

Version: 1.1

Purpose:

Apply implementation review findings before ERD generation.

---

# Unique Constraint Rules

## ActivityInstance

Previous:

code UNIQUE

---

Revised:

UNIQUE(project_id, code)

UNIQUE(project_id, wbs_item_id, location_id)

---

Reason:

ActivityInstance codes may repeat across projects.

Example:

Project A

COLUMN-C5

---

Project B

COLUMN-C5

---

Both are valid.

---

## WorkflowStep

Add:

UNIQUE(activity_instance_id, code)

---

Reason:

WorkflowStep codes only need to be unique inside an ActivityInstance.

Example:

Column C5

↓

REBAR

FORMWORK

CONCRETE

---

## WorkOrder

Previous:

work_order_number UNIQUE

---

Revised:

UNIQUE(project_id, work_order_number)

---

Reason:

WorkOrder numbering should be unique inside a project.

Not globally.

---

# WorkflowStep Rules

## ready

Type:

BOOLEAN

Default:

FALSE

---

Rule:

ready is a computed field.

ready is not manually editable.

---

Ready is calculated from:

- required documents
- required permits
- predecessor completion
- required resources
- required approvals

---

Ready

≠

Status

---

## planned_weight

Type:

NUMERIC(8,2)

Nullable:

Yes

---

Description:

Relative workflow contribution to ActivityInstance progress.

---

Constraints:

planned_weight >= 0

planned_weight <= 100

---

Purpose:

Used for ActivityInstance progress rollup.

---

# WorkOrder Relationship Revision

Previous Assumption:

WorkflowStep

1:N

WorkOrder

---

Final Decision:

WorkflowStep

N:N

WorkOrder

---

Reason:

A WorkOrder may contain multiple WorkflowSteps.

A WorkflowStep may be executed through multiple WorkOrders.

Example:

WorkOrder 2026-06-10

↓

Rebar C5

Rebar C6

Masonry W12

---

Example:

Rebar C5

↓

WO-01

WO-02

WO-03

---

# WorkOrder WorkflowStep Mapping

Table:

work_order_workflow_steps

Purpose:

Junction table between WorkOrders and WorkflowSteps.

---

## id

Type:

UUID

Nullable:

No

---

## work_order_id

Type:

UUID

Nullable:

No

FK:

work_[orders.id](http://orders.id)

---

## workflow_step_id

Type:

UUID

Nullable:

No

FK:

workflow_[steps.id](http://steps.id)

---

## execution_weight

Type:

NUMERIC(8,2)

Nullable:

No

---

Description:

Contribution of this WorkOrder toward WorkflowStep completion.

---

Constraints

execution_weight > 0

execution_weight <= 100

---

Workflow Progress

=

Σ Completed WorkOrder Weights

/

Total Workflow Weight

---

# Canonical Cardinality

ActivityInstance

1:N

WorkflowStep

---

WorkflowStep

N:N

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

BOQItem

1:N

BOQMapping

---

# ERD Readiness Status

Architecture Consistency:

95%

---

Database Readiness:

90%

---

ERD Readiness:

95%

---

Implementation Blockers:

None

---

Next Phase:

ERD v1

↓

PostgreSQL Schema Design

↓

Backend Entity Modeling

---

# Project

## Table

projects

---

## Primary Key

id

Type:

UUID

Nullable:

No

Description:

Unique project identifier.

---

## code

Type:

VARCHAR(100)

Nullable:

No

Unique:

Yes

Description:

Project code.

Example:

PRJ-001

---

## name

Type:

VARCHAR(255)

Nullable:

No

Description:

Project name.

---

## description

Type:

TEXT

Nullable:

Yes

---

## status

Type:

VARCHAR(50)

Nullable:

No

Default:

ACTIVE

Allowed Values:

- DRAFT
- ACTIVE
- ON_HOLD
- COMPLETED
- CANCELLED

---

## planned_start

Type:

DATE

Nullable:

Yes

---

## planned_finish

Type:

DATE

Nullable:

Yes

---

## created_at

Type:

TIMESTAMP

Nullable:

No

---

## updated_at

Type:

TIMESTAMP

Nullable:

No

---

# Database Constraints

UNIQUE(code)

---

name IS REQUIRED

---

# WBSItem

## Table

wbs_items

---

## Primary Key

id

Type:

UUID

Nullable:

No

---

## project_id

Type:

UUID

Nullable:

No

FK:

[projects.id](http://projects.id)

---

## parent_id

Type:

UUID

Nullable:

Yes

FK:

wbs_[items.id](http://items.id)

Description:

Supports hierarchical WBS structures.

---

## code

Type:

VARCHAR(100)

Nullable:

No

Description:

WBS code.

Example:

1.2.3

---

## name

Type:

VARCHAR(255)

Nullable:

No

---

## description

Type:

TEXT

Nullable:

Yes

---

## level

Type:

INTEGER

Nullable:

No

Description:

Hierarchy level.

---

## status

Type:

VARCHAR(50)

Nullable:

No

Default:

ACTIVE

Allowed Values:

- ACTIVE
- COMPLETED
- CANCELLED

---

## created_at

Type:

TIMESTAMP

Nullable:

No

---

## updated_at

Type:

TIMESTAMP

Nullable:

No

---

# Database Constraints

UNIQUE(project_id, code)

---

parent_id references wbs_[items.id](http://items.id)

---

# Location

## Table

locations

---

## Primary Key

id

Type:

UUID

Nullable:

No

---

## project_id

Type:

UUID

Nullable:

No

FK:

[projects.id](http://projects.id)

---

## parent_id

Type:

UUID

Nullable:

Yes

FK:

[locations.id](http://locations.id)

Description:

Supports location hierarchy.

---

## code

Type:

VARCHAR(100)

Nullable:

No

Example:

F3-C5

---

## name

Type:

VARCHAR(255)

Nullable:

No

Example:

Floor 3 / Axis C5

---

## description

Type:

TEXT

Nullable:

Yes

---

## level

Type:

INTEGER

Nullable:

No

Description:

Hierarchy depth.

---

## status

Type:

VARCHAR(50)

Nullable:

No

Default:

ACTIVE

Allowed Values:

- ACTIVE
- CLOSED

---

## created_at

Type:

TIMESTAMP

Nullable:

No

---

## updated_at

Type:

TIMESTAMP

Nullable:

No

---

# Database Constraints

UNIQUE(project_id, code)

---

parent_id references [locations.id](http://locations.id)

---

# WorkflowStepTemplate

## Table

workflow_step_templates

---

## Primary Key

id

Type:

UUID

Nullable:

No

---

## code

Type:

VARCHAR(100)

Nullable:

No

Unique:

Yes

---

## name

Type:

VARCHAR(255)

Nullable:

No

Examples:

- Rebar
- Formwork
- Concrete

---

## description

Type:

TEXT

Nullable:

Yes

---

## method_statement

Type:

TEXT

Nullable:

Yes

Description:

Execution methodology.

---

## safety_requirements

Type:

TEXT

Nullable:

Yes

Description:

Safety instructions.

---

## inspection_checklist

Type:

TEXT

Nullable:

Yes

Description:

Quality checklist.

---

## required_resources

Type:

JSONB

Nullable:

Yes

Description:

Resource requirements.

---

## required_permits

Type:

JSONB

Nullable:

Yes

Description:

Permit requirements.

---

## required_documents

Type:

JSONB

Nullable:

Yes

Description:

Required execution documents.

---

## execution_guide

Type:

TEXT

Nullable:

Yes

Description:

Training and execution guidance.

---

## standard_references

Type:

TEXT

Nullable:

Yes

Description:

Referenced standards and codes.

---

## status

Type:

VARCHAR(50)

Nullable:

No

Default:

ACTIVE

Allowed Values:

- ACTIVE
- ARCHIVED

---

## created_at

Type:

TIMESTAMP

Nullable:

No

---

## updated_at

Type:

TIMESTAMP

Nullable:

No

---

# Database Constraints

UNIQUE(code)

---

Templates are reusable across projects.

---

Templates are knowledge sources.

---

WorkflowSteps are generated from template snapshots.

---

Template updates do not modify existing WorkflowSteps.