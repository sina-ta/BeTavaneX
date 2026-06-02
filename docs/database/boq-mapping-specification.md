# BOQ Mapping Specification

Status: Approved

Version: 1.0

---

# Purpose

Define how WorkflowSteps are connected to BOQItems.

BOQMapping provides the bridge between:

Execution Reality

and

Financial Measurement Reality.

BOQMapping enables:

- cost allocation
- quantity allocation
- earned value calculation
- financial visibility

while preserving separation between execution and financial domains.

---

# Core Principle

WorkflowSteps represent execution reality.

BOQItems represent financial reality.

BOQMappings connect the two domains.

---

Execution Reality

↓

WorkflowStep

↓

BOQMapping

↓

BOQItem

↓

Financial Reality

---

# Why BOQMapping Exists

Direct linkage between WorkflowStep and BOQItem creates ambiguity.

Examples:

One WorkflowStep may consume:

- Rebar Installation
- Rebar Couplers
- Embedded Plates

Multiple BOQItems may contribute to a single WorkflowStep.

Likewise:

One BOQItem may be distributed across multiple WorkflowSteps.

BOQMapping resolves this allocation problem.

---

# Relationship Model

WorkflowStep

1:N

BOQMapping

---

BOQItem

1:N

BOQMapping

---

BOQMapping is an associative entity.

---

# Core Attributes

id

workflow_step_id

boq_item_id

allocated_quantity

allocated_cost

allocation_percentage

allocated_weight

notes

created_at

updated_at

---

# Attribute Definitions

## workflow_step_id

Reference to WorkflowStep.

Defines execution ownership.

---

## boq_item_id

Reference to BOQItem.

Defines financial ownership.

---

## allocated_quantity

Quantity of BOQItem allocated to the WorkflowStep.

Example:

BOQ Item:

Rebar Installation

1000 kg

---

WorkflowStep:

Rebar @ Column C5

Allocated Quantity:

100 kg

---

## allocated_cost

Financial value allocated to the WorkflowStep.

Formula:

Allocated Quantity

×

BOQ Rate

---

## allocation_percentage

Percentage of BOQItem assigned to the WorkflowStep.

Example:

100 kg

/

1000 kg

=

10%

---

## allocated_weight

Relative contribution of this BOQMapping to financial valuation.

Used for:

- earned value
- cost visibility
- future financial analytics

---

# Quantity Allocation Model

Example:

BOQ Item

Rebar Installation

1000 kg

---

Distributed to:

Rebar @ C1

100 kg

---

Rebar @ C2

120 kg

---

Rebar @ C3

80 kg

---

Remaining WorkflowSteps

700 kg

---

Each allocation is stored independently.

---

# Cost Allocation Model

BOQ Item:

Quantity = 1000 kg

Rate = 1000

---

WorkflowStep:

Allocated Quantity = 100 kg

---

Allocated Cost

=

100 × 1000

=

100,000

---

# Workflow Cost Calculation

WorkflowStep Planned Cost

=

Σ Allocated Costs

from BOQMappings

---

Example

WorkflowStep

↓

BOQMapping A

50,000

---

BOQMapping B

30,000

---

Workflow Planned Cost

=

80,000

---

# Activity Cost Calculation

ActivityInstance Planned Cost

=

Σ WorkflowStep Planned Costs

---

# Project Cost Calculation

Project Planned Cost

=

Σ ActivityInstance Planned Costs

---

# Earned Value Integration

BOQMapping provides valuation inputs.

Workflow Progress remains operational.

Workflow Progress

↓

BOQMapping

↓

Allocated Cost

↓

Earned Value

---

Formula

Earned Value

=

Workflow Progress

×

Workflow Planned Cost

---

# Progress Separation Principle

BOQMappings do not create progress.

WorkflowSteps create progress.

BOQMappings only provide valuation.

This separation is intentional.

---

# Phase 1 Simplification

Phase 1 uses:

Commitment-Based Progress

Workflow Progress

=

Completed WorkOrder Weights

/

Total Workflow Weight

BOQMappings use workflow progress for valuation purposes only.

---

# Future Extensions

Future versions may introduce:

- actual quantity tracking
- quantity verification
- quantity reconciliation
- material consumption tracking
- labor cost allocation
- equipment cost allocation
- automated earned value calculations

BOQMapping remains the integration point.

---

# Ownership Rules

BOQMapping owns:

- quantity allocation
- cost allocation
- valuation linkage

---

BOQMapping does not own:

- execution
- progress
- inspections
- approvals
- blockers

---

# Strategic Position

Construction Reality

↓

ActivityInstance

---

Execution Reality

↓

WorkflowStep

---

Execution-Financial Integration

↓

BOQMapping

---

Financial Measurement Reality

↓

BOQItem

---

Cost Visibility

↓

Earned Value

↓

Financial Intelligence

---

# Architectural Principle

BetavanX intentionally separates:

Construction Reality

Execution Reality

Financial Reality

BOQMapping is the controlled integration point between execution and finance.

This separation enables:

- operational simplicity
- financial visibility
- earned value analysis
- future cost intelligence
- scalable architecture

