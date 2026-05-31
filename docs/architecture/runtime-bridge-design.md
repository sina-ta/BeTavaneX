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
+  
Location  
+  
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
+  
Location  
+  
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