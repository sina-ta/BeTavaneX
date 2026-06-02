# BetavanX ERD v1

Status: Approved

Version: 1.0

Purpose:

Define the canonical Entity Relationship Diagram (ERD) for BetavanX Phase 1.

This ERD represents the database structure derived from:

- Runtime Core Architecture
- Entity Catalog
- Relationship Matrix
- Data Dictionary

---

# Planning Layer

Project

├── WBSItem

├── Location

└── BOQItem

---

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

# Construction Reality Layer

WBSItem

1:N

ActivityInstance

---

Location

1:N

ActivityInstance

---

ActivityInstance

N:1

Project

---

ActivityInstance

1:N

WorkflowStep

---

# Execution Knowledge Layer

WorkflowStepTemplate

1:N

WorkflowStep

(Snapshot Source)

---

# Execution Layer

WorkflowStep

N:N

WorkOrder

(via work_order_workflow_steps)

---

WorkOrder

1:N

DailyReport

---

# Quality Layer

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

WorkflowStep

1:N

Blocker

---

# Financial Layer

WorkflowStep

1:N

BOQMapping

---

BOQItem

1:N

BOQMapping

---

# Resource Layer

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

# Canonical ERD

Project  
│  
├── WBSItem  
│  
├── Location  
│  
├── BOQItem  
│  
└── ActivityInstance  
│  
└── WorkflowStep  
│  
├── Inspection  
│ │  
│ └── PunchItem  
│  
├── Approval  
│  
├── Blocker  
│  
├── BOQMapping  
│ │  
│ └── BOQItem  
│  
└── WorkOrder  
│  
└── DailyReport

---

# Junction Tables

## work_order_workflow_steps

WorkOrder

N:N

WorkflowStep

---

Stores:

- work_order_id
- workflow_step_id
- execution_weight

---

# Future Junction Tables

Potential future tables:

workflow_step_resources

workflow_step_crews

workflow_step_materials

workflow_step_equipment

These are not required for Phase 1 implementation.

---

# Primary Foreign Keys

ActivityInstance

- project_id
- wbs_item_id
- location_id

---

WorkflowStep

- activity_instance_id
- workflow_template_id

---

WorkOrderWorkflowStep

- work_order_id
- workflow_step_id

---

DailyReport

- work_order_id

---

Inspection

- workflow_step_id

---

PunchItem

- inspection_id
- workflow_step_id

---

Approval

- workflow_step_id

Approval depends on Inspection and PunchItem outcomes at application level.

Approval has no direct foreign key relationships with Inspection or PunchItem.

---

Blocker

- workflow_step_id

---

BOQMapping

- workflow_step_id
- boq_item_id

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

↓

Approval

---

# Financial Hierarchy

BOQItem

↓

BOQMapping

↓

WorkflowStep

---

# Architectural Principle

BetavanX intentionally separates:

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

Financial Integration

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

This ERD forms the foundation of the BetavanX PostgreSQL schema.