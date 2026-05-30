# BetavanX — Operational Capability Model

**Status:** Partial

Some capabilities are active in runtime MVP (KPI, validation, lifecycle, recommendations).
Full graph-native capability integration is target architecture.

**Terminology:** Capabilities operate on operational execution entities.
Canonical data entity: **Activity Instance** (`glossary.md`).
**Operational Task** is the user-facing label.

---

Operational capabilities are NOT construction deliverables.

They are:

# Platform Operational Intelligence Layers

These capabilities continuously monitor,
analyze,
control,
and react to operational project behavior.

---

# Capability Categories

## 01 Operational Controls

01.01 Progress Tracking
01.02 Delay Monitoring
01.03 Constraint Tracking
01.04 Dependency Monitoring
01.05 Resource Monitoring
01.06 Productivity Monitoring
01.07 Operational Alerts

---

## 02 Scheduling & Planning Intelligence

02.01 Dynamic Scheduling
02.02 Workflow Suggestions
02.03 Parallel Execution Detection
02.04 Critical Path Monitoring
02.05 Reactive Rescheduling
02.06 Lookahead Planning
02.07 Schedule Forecasting

---

## 03 Resource Intelligence

03.01 Manpower Allocation
03.02 Equipment Allocation
03.03 Material Tracking
03.04 Resource Conflict Detection
03.05 Resource Forecasting
03.06 Productivity Analysis

---

## 04 Quality & Safety Controls

04.01 Inspection Tracking
04.02 NCR Monitoring
04.03 Hold Point Tracking
04.04 Safety Monitoring
04.05 Permit Monitoring
04.06 Incident Tracking

---

## 05 Operational Analytics

05.01 Progress Analytics
05.02 Delay Analytics
05.03 Productivity Analytics
05.04 Cost Analytics
05.05 Risk Analytics
05.06 Operational KPI Monitoring

---

## 06 Reporting & Visibility

06.01 Daily Reporting
06.02 Dashboard Visualization
06.03 Executive Reporting
06.04 Investor Visibility
06.05 Site Visibility
06.06 Operational History

---

## 07 Forecasting & Decision Support

07.01 Delay Forecasting
07.02 Completion Forecasting
07.03 Operational Recommendations
07.04 Resource Recommendations
07.05 Risk Forecasting
07.06 Operational Decision Support

---

## 08 Digital Construction & Platform Intelligence

**Relocated from WBS Phase 16** (`wbs-template-library.md` reconciliation).

These are platform capabilities — not construction deliverables:

08.01 Data Governance
08.02 KPI Dashboards
08.03 Workflow Automation
08.04 Operational Analytics
08.05 Forecasting

Do not place these items in the WBS construction taxonomy.

---

# Capability Philosophy

Capabilities are:

* dynamic
* reactive
* operational
* graph-aware
* data-driven

They operate on top of:

# Activity Instances

(in target architecture)

In current runtime MVP, capabilities primarily operate on **Daily Work Orders**
and **Daily Reports** until the Operational Graph is integrated.

Capabilities do NOT replace operational execution.

They enhance:

* visibility
* monitoring
* coordination
* forecasting
* operational control

---

# Architectural Principle

Construction deliverables belong to:

# Construction WBS

Operational intelligence behaviors belong to:

# Operational Capability Layer

This separation keeps BetavanX:

* modular
* scalable
* extensible
* operationally coherent

WITHOUT collapsing into ERP complexity.

---

# Final Capability Identity

BetavanX capabilities continuously transform:

* operational data
* execution history
* progress logs
* workflow behavior
* resource conditions
* field events

into:

* operational visibility
* reactive scheduling
* execution intelligence
* decision support
* project forecasting
* operational analytics
