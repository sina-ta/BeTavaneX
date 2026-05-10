# BetavanX Database Schema v1

---

# DailyWorkOrder

| Field | Type | Description |
|---|---|---|
| id | UUID | Unique ID |
| project_id | UUID | Related project |
| task_id | UUID | Related task |
| assigned_to | UUID | Responsible person/team |
| planned_qty | Float | Planned quantity |
| unit | String | Unit of measurement |
| planned_start | Datetime | Planned start |
| planned_finish | Datetime | Planned finish |
| priority | Enum | Low / Medium / High / Critical |
| status | Enum | Open / In Progress / Completed |
| created_by | UUID | Creator |
| created_at | Datetime | Creation timestamp |

---

# DailyReport

| Field | Type | Description |
|---|---|---|
| id | UUID | Unique ID |
| work_order_id | UUID | Related work order |
| reported_by | UUID | Reporter |
| actual_qty | Float | Executed quantity |
| manpower_count | Integer | Number of workers |
| equipment_hours | Float | Equipment usage |
| material_consumption | Float | Material used |
| delay_reason | Text | Delay explanation |
| weather_status | String | Weather condition |
| photo_count | Integer | Attached photos |
| report_status | Enum | Draft / Submitted / Approved |
| submitted_at | Datetime | Submission timestamp |
| approved_by | UUID | Supervisor approval |

---

# Core Relationship

Task
→ DailyWorkOrder
→ DailyReport

---

# Key Principle

Reports are not independent records.

Reports are responses to planned work orders.