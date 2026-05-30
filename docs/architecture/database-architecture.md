# BetavanX Database Architecture

**Status:** Partial (document outdated vs current schema — pending rewrite)

Canonical runtime reference: `current-vs-target-architecture.md`

---

## Database Engine

Primary database:

- PostgreSQL

The database is designed for scalable enterprise construction management systems.

---

# Database Philosophy

The database architecture is designed for:

- scalability
- modularity
- analytics readiness
- BIM integrations
- workforce intelligence
- operational tracking
- future AI systems

---

# Core Database Domains

The database is separated into several logical domains.

---

# Main Domains

## Workforce Domain

Responsible for:

- workers
- crews
- attendance
- performance
- skills
- HR tracking

Main tables:

- workers
- crews
- worker_skills
- attendance_logs
- worker_performance

---

## Operations Domain

Responsible for:

- daily reports
- work orders
- project activities
- progress tracking

Main tables:

- daily_reports
- work_orders
- tasks
- task_progress
- field_activities

---

## Financial Domain

Responsible for:

- costs
- wages
- productivity
- budget tracking

Main tables:

- labor_costs
- equipment_costs
- material_costs
- project_budgets
- payment_logs

---

## Equipment Domain

Responsible for:

- machinery
- usage tracking
- maintenance
- operational hours

Main tables:

- equipment
- equipment_usage
- maintenance_logs

---

## BIM Integration Domain

Responsible for:

- BIM elements
- model mapping
- construction linking
- object relationships

Main tables:

- bim_objects
- bim_tasks
- model_versions
- object_relations

---

# Database Design Principles

## 1. UUID-Based IDs

Most tables should eventually use UUIDs for scalability and distributed systems.

---

## 2. Timestamp Tracking

All major tables should include:

- created_at
- updated_at

Some systems may also require:

- deleted_at

for soft deletes.

---

## 3. Relationship-Driven Structure

The database is highly relational.

Examples:

- workers linked to crews
- tasks linked to reports
- reports linked to projects
- BIM objects linked to tasks

---

## 4. Analytics Ready

The schema is designed to support:

- KPI calculations
- productivity analysis
- forecasting
- AI recommendations
- historical trend analysis

---

# Current Existing Tables

Current implemented tables:

- workers
- daily_reports
- work_orders
- tasks

---

# Planned Future Tables

Future planned systems:

- notifications
- audit_logs
- user_roles
- permissions
- equipment_tracking
- AI_recommendations
- BIM_sync_logs
- project_snapshots

---

# Long-Term Goal

The database should evolve into a scalable construction intelligence data platform capable of supporting:

- enterprise ERP systems
- BIM-connected workflows
- real-time monitoring
- predictive analytics
- workforce intelligence
- AI-assisted decision systems

---

# Foundational Principle

The database is fundamentally designed around operational daily reporting.

Daily reports are considered the primary source of operational truth.

Most analytics, intelligence systems, KPIs, and future AI systems are derived from daily operational reporting data.