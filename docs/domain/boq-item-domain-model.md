# BOQ Item Domain Model

Status: Approved

Version: 1.1

---

# Purpose

Define the BOQItem entity of BetavanX.

BOQItem represents the financial measurement unit used for planning, valuation, earned value calculation, financial visibility, and future cost intelligence.

BOQItem is the bridge between execution reality and financial reality.

---

# Definition

BOQItem

=

Bill Of Quantity Item

A BOQItem defines a measurable unit of work together with its commercial value.

Examples:

* Rebar Installation
* Concrete Placement
* Formwork Installation
* Masonry Work
* Waterproofing

---

# Core Principle

BOQItems represent financial measurement reality.

BOQItems do not represent construction reality.

BOQItems do not represent execution reality.

---

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

# Examples

Example:

BOQ Item:

Rebar Installation

Unit:

kg

Quantity:

100

Rate:

1,000

Planned Cost:

100,000

---

Example:

Concrete Placement

Unit:

m³

Quantity:

20

Rate:

2,500

Planned Cost:

50,000

---

# BOQ Ownership

BOQItems own:

* measurement units
* quantities
* rates
* planned values
* valuation rules

BOQItems do not own execution.

BOQItems do not own workflow states.

BOQItems do not own inspections.

BOQItems do not own approvals.

---

# Relationships

## Project Relationship

Project

1:N

BOQItem

A project contains many BOQItems.

---

## Workflow Relationship

WorkflowStep

1:N

BOQMapping

---

BOQItem

1:N

BOQMapping

---

A WorkflowStep may be linked to multiple BOQItems.

A BOQItem may contribute to multiple WorkflowSteps.

---

# BOQMapping Purpose

BOQMapping defines the relationship between:

WorkflowStep

and

BOQItem

BOQMapping may contain:

* quantity allocation
* valuation linkage
* cost allocation

BOQMapping is an associative entity.

---

# Mapping Principle

WorkflowStep

↓

BOQMapping

↓

BOQItem

Financial measurement is linked through BOQ mappings.

---

# Example

WorkflowStep:

Rebar @ C5

↓

BOQMapping

↓

BOQ Item:

Rebar Installation

Quantity:

100 kg

Rate:

1,000

---

Planned Cost:

100,000

---

# Cost Principle

WorkflowStep planned cost originates from BOQItems.

Formula:

Planned Cost

=

Quantity × Rate

---

# ActivityInstance Cost

ActivityInstance Cost

=

Sum of WorkflowStep Planned Costs

---

# Project Cost

Project Cost

=

Sum of ActivityInstance Costs

---

# Progress Relationship

Phase 1 operational progress is not calculated from BOQ quantities.

Phase 1 progress is derived from completed WorkOrder Weights.

BOQItems provide the valuation basis for earned value calculations.

Operational progress and financial valuation are intentionally separated.

---

# Example

WorkflowStep Cost:

100,000

Workflow Progress:

33%

↓

Earned Value:

33,000

---

# Earned Value Principle

Earned Value

=

Workflow Progress

×

Planned Cost

---

Phase 1 Workflow Progress is defined by:

Completed WorkOrder Weights

as described in:

runtime-bridge-design.md

BOQItems use workflow progress for valuation purposes only.

---

BOQItems provide the planned value required for earned value calculations.

---

# Phase 1 Scope

Phase 1 BOQItems support:

* planned quantity
* unit rate
* planned value
* earned value
* financial visibility

Phase 1 does not support:

* actual labor cost
* actual equipment cost
* actual material consumption
* actual indirect cost

---

# Future Cost Intelligence Relationship

Future versions may extend BOQItems through:

* resource consumption
* labor tracking
* equipment tracking
* material tracking
* actual cost calculation

BOQItems remain the financial measurement layer.

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

Financial Measurement Reality

↓

BOQItem

---

Cost Visibility

↓

Earned Value

↓

Cost Intelligence

---

# Strategic Alignment

BOQItems provide the financial foundation for:

* earned value analysis
* financial visibility
* progress valuation
* budget visibility
* future cost intelligence

BOQItem is the primary financial measurement entity of BetavanX.

---

# Architectural Principle

Execution and financial measurement are intentionally separated.

WorkflowSteps represent execution reality.

BOQItems represent financial reality.

BOQMappings connect the two domains.

This separation enables:

* operational simplicity
* financial visibility
* future cost intelligence
* scalable architecture
