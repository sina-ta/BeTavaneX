# Workflow Step Domain Model

Status: Approved

Version: 1.1

---

# Purpose

Define the canonical execution entity of BetavanX.

WorkflowStep represents a measurable execution stage required to complete an ActivityInstance.

WorkflowSteps are the primary execution management entities of BetavanX.

---

# Definition

WorkflowStep

=

Execution Reality

A WorkflowStep represents actual construction execution.

Examples:

* Rebar
* Formwork
* Concrete
* Masonry
* Waterproofing

---

# Core Principle

ActivityInstance represents:

Construction Reality

WorkflowStep represents:

Execution Reality

WorkflowStep is where:

* execution occurs
* progress is measured
* inspections occur
* approvals occur
* blockers occur
* work orders are generated

---

# WorkflowStep Template Relationship

WorkflowSteps are generated from WorkflowStepTemplates.

WorkflowStepTemplate

↓

Snapshot

↓

WorkflowStep

WorkflowSteps inherit execution knowledge from WorkflowStepTemplates.

WorkflowSteps do NOT maintain live references to templates.

This preserves:

* historical accuracy
* auditability
* building memory
* legal traceability

---

# WorkflowStepTemplate Provides

WorkflowStepTemplates define:

* execution method
* training material
* execution guides
* safety requirements
* inspection checklists
* applicable standards
* required permits
* required documents
* required trades
* required tools
* required equipment
* BOQ mappings
* productivity rules
* typical drawings

---

# WorkflowStep Ownership

WorkflowStep owns:

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
* execution requirements
* BOQ mappings

WorkflowStep is the primary operational entity of BetavanX.

---

# Execution Requirements

WorkflowStep execution may require:

* drawings
* permits
* approvals
* materials
* resources
* documents

Execution requirements are evaluated before execution begins.

---

# Ready Principle

Ready

≠

Status

Ready

=

Computed Condition

Ready is calculated.

Ready is not a lifecycle state.

---

# Ready Evaluation

Ready may depend on:

* required drawings available
* required permits available
* required approvals completed
* required materials available
* required resources assigned
* required documents available
* previous workflow approved

Example:

Concrete

requires

Rebar Approved

before becoming Ready.

---

# Blocker Principle

Blocked

≠

Not Ready

---

Not Ready

=

Required execution conditions are not satisfied.

Examples:

* missing permit
* missing drawing
* missing approval
* missing resource assignment

---

Blocked

=

Unexpected operational conditions prevent execution despite planning readiness.

Examples:

* weather
* equipment failure
* access restrictions
* labor strike
* material delivery failure
* stop work order

---

# Lifecycle Model

WorkflowStep lifecycle:

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

# Failure Path

Inspection Failed

↓

Rework Required

↓

In Progress

---

# Progress Ownership

WorkflowStep owns progress.

ActivityInstance aggregates progress.

Projects aggregate ActivityInstance progress.

---

# Progress Model

Phase 1 Progress is commitment-based.

Workflow Progress is derived from completed WorkOrders.

Progress does not rely on measured physical quantities.

This decision is intentional to maximize field adoption and simplify operational reporting.

---

Workflow Progress

=

Σ Completed WorkOrder Weights

/

Total Workflow Weight

---

Example

WO-1 = 33%

WO-2 = 33%

WO-3 = 34%

---

WO-1 Completed

↓

Workflow Progress = 33%

---

WO-2 Completed

↓

Workflow Progress = 66%

---

WO-3 Completed

↓

Workflow Progress = 100%

---

# Progress vs Approval

Progress and Approval are independent concepts.

Workflow Progress may reach 100% before approval.

Examples:

Workflow Progress = 100%

Status = Inspection Pending

or

Status = Approval Pending

Both situations are valid.

Progress measures execution completion.

Approval measures acceptance.

Completed does not imply Approved.

---

# BOQ Relationship

WorkflowStep owns BOQ mappings.

WorkflowStep

↓

BOQ Mapping

↓

BOQ Item

BOQ is not owned by ActivityInstance.

---

# Cost Relationship

WorkflowStep owns planned cost relationships.

WorkflowStep cost originates from:

BOQ Quantity

×

BOQ Rate

ActivityInstance cost is aggregated from WorkflowSteps.

---

# Resource Ownership

WorkflowStep owns resource assignments.

Examples:

* crews
* contractors
* supervisors
* equipment
* materials

Resource ownership belongs to WorkflowStep.

Resource ownership does not belong to WorkOrder.

---

# WorkOrder Relationship

WorkflowStep

1:N

WorkOrder

A WorkflowStep may generate many WorkOrders.

Example:

Rebar @ C5

↓

WO-1

WO-2

WO-3

---

# WorkOrder Principle

WorkOrders are execution slices.

WorkOrders are not execution owners.

WorkOrders are not operational truth.

WorkOrders are execution coordination tools.

---

# Inspection Relationship

WorkflowStep

1:N

Inspection

A WorkflowStep may be inspected multiple times.

Example:

Inspection #1

Failed

↓

Inspection #2

Passed

---

# Approval Relationship

WorkflowStep

1:N

Approval

Phase 1 uses a simplified approval model.

A single final approval confirms successful workflow completion.

Future versions may support:

* survey approval
* consultant approval
* client approval
* authority approval

---

# Blocker Relationship

WorkflowStep

1:N

Blocker

Blockers record unexpected execution constraints.

---

# Strategic Position

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

# Strategic Alignment

WorkflowStep enables:

* execution visibility
* operational accountability
* progress measurement
* quality verification
* building memory

WorkflowStep is the primary execution entity of BetavanX Phase 1.
