# PostgreSQL Schema V1

Status: Draft

Version: 1.0

Purpose:

Define the initial PostgreSQL schema structure for BetavanX Phase 1.

This document translates the approved ERD and Data Dictionary into database implementation structures.

---

# Schema Philosophy

The PostgreSQL schema follows the BetavanX architectural layers:

Planning Layer

↓

Construction Reality Layer

↓

Execution Reality Layer

↓

Execution Coordination Layer

↓

Execution Evidence Layer

↓

Quality Layer

↓

Financial Layer

---

# Naming Convention

Tables:

snake_case

Examples:

activity_instances

workflow_steps

daily_reports

---

Primary Keys:

id UUID

---

Foreign Keys:

{entity}_id

Examples:

project_id

workflow_step_id

inspection_id

---

Audit Fields:

created_at

updated_at

---

# Planning Layer Tables

## projects

Purpose:

Root project entity.

---

## wbs_items

Purpose:

Project work breakdown structure.

---

## locations

Purpose:

Project location hierarchy.

---

## boq_items

Purpose:

Financial measurement items.

---

# Construction Reality Tables

## activity_instances

Purpose:

Construction scope plus planning commitment.

Relationships:

- project_id
- wbs_item_id
- location_id

Constraints:

- UNIQUE(project_id, code)
- UNIQUE(project_id, wbs_item_id, location_id)

ActivityInstance status values:

- ACTIVE
- COMPLETED
- CANCELLED

---

# Execution Knowledge Tables

## workflow_step_templates

Purpose:

Reusable execution knowledge.

Examples:

- Rebar
- Formwork
- Concrete

---

# Execution Reality Tables

## workflow_steps

Purpose:

Primary execution entity.

Relationships:

- activity_instance_id
- workflow_template_id

Owns:

- progress
- readiness
- inspections
- approvals
- blockers

WorkflowStep status values:

- PLANNED
- IN_PROGRESS
- COMPLETED
- INSPECTION_PENDING
- INSPECTION_FAILED
- REWORK_REQUIRED
- APPROVED

READY is not a status.

READY is a computed condition represented by `ready BOOLEAN`.

Derived fields:

- earned_value (not persisted)
- earned_value = Workflow Progress × Planned Cost

---

# Execution Coordination Tables

## work_orders

Purpose:

Execution coordination packages.

---

## work_order_workflow_steps

Purpose:

Junction table.

Relationships:

- work_order_id
- workflow_step_id

Owns:

- execution_weight

Constraints:

- UNIQUE(work_order_id, workflow_step_id)

---

# Execution Evidence Tables

## daily_reports

Purpose:

Execution evidence.

Relationships:

- work_order_id

Additional field:

- evidence_metadata JSONB NULL (stores photos, attachments, documents, observations)

---

# Quality Tables

## inspections

Purpose:

Quality verification.

Relationships:

- workflow_step_id

---

## punch_items

Purpose:

Quality findings.

Relationships:

- inspection_id
- workflow_step_id

---

## approvals

Purpose:

Operational acceptance.

Relationships:

- workflow_step_id

Approval depends on Inspection and PunchItem outcomes.

Approval does not maintain direct foreign key relationships with Inspection or PunchItem.

Approval dependencies are enforced at application level.

---

# Operational Constraint Tables

## blockers

Purpose:

Execution constraints.

Relationships:

- workflow_step_id

---

# Financial Integration Tables

## boq_mappings

Purpose:

Bridge between execution and finance.

Relationships:

- workflow_step_id
- boq_item_id

Owns:

- allocated_quantity
- allocated_cost

Constraints:

- UNIQUE(workflow_step_id, boq_item_id)

---

# User Reference Policy (Phase 1)

For `created_by`, `submitted_by`, `approved_by`, `assigned_to`, and `reported_by`:

- Phase 1 stores user UUID references only
- No users table exists in Phase 1
- No foreign key enforcement is applied
- Future versions may introduce a users table

---

# Future Resource Tables

Not required for Phase 1.

Potential future tables:

- resources
- crews
- equipment
- materials
- contractors
- supervisors
- workflow_step_resources
- workflow_step_crews
- workflow_step_materials
- workflow_step_equipment

---

# Phase 1 Core Tables

projects

wbs_items

locations

boq_items

activity_instances

workflow_step_templates

workflow_steps

work_orders

work_order_workflow_steps

daily_reports

inspections

punch_items

approvals

blockers

boq_mappings

---

# Database Principles

Construction Reality

↓

activity_instances

---

Execution Reality

↓

workflow_steps

---

Execution Coordination

↓

work_orders

---

Execution Evidence

↓

daily_reports

---

Quality Verification

↓

inspections

↓

punch_items

---

Operational Approval

↓

approvals

---

Operational Constraints

↓

blockers

---

Financial Reality

↓

boq_items

---

Financial Integration

↓

boq_mappings

---

# Implementation Readiness

Architecture:

Complete

---

ERD:

Complete

---

Schema Structure:

Defined

---

Next Phase:

Physical Database Design

↓

Migration Generation

↓

Backend Entity Models

↓

API Development