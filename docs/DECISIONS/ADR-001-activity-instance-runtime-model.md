# ADR-001 — Activity Instance Runtime Model

Status: Accepted

Date: 2026

---

# Context

BetavanX is a Building Lifecycle Intelligence Platform entering the market through Construction Visibility.

A runtime audit identified ambiguity between:

- Activity Instance
- Workflow Step
- Daily Work Order
- Daily Report

This document defines the canonical relationship between these concepts.

---

# Decision

Activity Instance is the canonical operational entity of BetavanX.

Activity Instance represents a real construction activity occurring at a specific location.

Examples:

- Concrete Column C5
- Masonry Wall W12
- HVAC Zone A-03

Activity Instances are created during Planning.

Creation occurs when:

WBS Item  
+  
Location

are instantiated into a real construction activity.

---

# Activity Instance

Activity Instance:

- exists independently of scheduling
- exists independently of resource assignments
- exists independently of work orders

Activity Instance is NOT:

- a schedule item
- a work order
- a daily report

Activity Instance represents construction reality.

---

# Workflow Steps

Workflow Steps belong to Activity Instances.

Example:

Activity Instance:

Concrete Column C5

Workflow Steps:

1. Rebar
2. Formwork
3. Concrete

Workflow Steps define execution stages.

---

# Daily Work Orders

Daily Work Orders belong to Workflow Steps.

Daily Work Orders are:

daily execution instructions.

Daily Work Orders are NOT operational truth.

A Workflow Step may generate multiple Daily Work Orders.

Example:

Workflow Step:

Rebar

Daily Work Orders:

- Install Rebar
- Continue Rebar
- Finish Rebar

---

# Daily Reports

Daily Reports belong to Daily Work Orders.

Daily Reports represent execution evidence.

Examples:

- quantities
- manpower
- weather
- notes
- photos
- issues

---

# Progress Model

Progress is derived from Daily Reports.

Aggregation path:

Daily Reports  
→ Workflow Step Progress  
→ Activity Instance Progress

Activity Instance Progress is the canonical progress representation.

---

# Building Memory

Building Memory is built around Activity Instances.

Future lifecycle records should attach to Activity Instances rather than Daily Work Orders.

Examples:

- inspections
- defects
- warranties
- maintenance history
- repairs
- renovations

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