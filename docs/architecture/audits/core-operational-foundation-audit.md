# Core Operational Foundation Audit

**Status:** Implemented (audit document)

**Audit type:** Architecture foundation audit — documentation only  
**Scope:** `backend/core_operational/` vs architecture docs  
**Date context:** Post documentation reconciliation sprint

**Reference documents:**

- `core-operational-model.md`
- `construction-execution-logic-model.md`
- `workflow-graph.md`
- `location-system.md`
- `architectural-separation-model.md`
- `glossary.md`
- `current-vs-target-architecture.md`
- `open-architecture-questions.md`

**Audit constraint:** No runtime code was modified. No features were proposed for implementation.

---

## Executive Summary

`backend/core_operational/` provides a **coherent foundational schema** for the target Operational Graph. It correctly separates WBS taxonomy, workflow possibility graph, location hierarchy, executable activities, activity dependencies, resources, assignments, and progress logs.

The foundation is **architecturally aligned** with BetavanX graph principles at the entity level, but **partially aligned** at relationship completeness, formal modeling depth, and runtime integration readiness.

| Area | Verdict |
|------|---------|
| Entity coverage | Strong — all 10 expected entities exist |
| WBS ≠ Schedule separation | Aligned |
| Activity Instance as canonical entity | Aligned |
| Workflow vs Dependency separation | Aligned |
| Workflow Context modeling | Misaligned (under-specified) |
| Constraint modeling | Misaligned (missing) |
| Runtime wiring | Not present (by design today) |
| Enum enforcement in schema | Partial |

---

## Package Overview

```
backend/core_operational/
├── models/entities.py      # SQLAlchemy entities (10)
├── schemas/operational.py  # Pydantic schemas
├── enums/operational_enums.py
├── relationships/map.py    # Conceptual relationship map
└── docs/README.md
```

**Integration state:**

- Models are **not imported** in `backend/api.py`
- Tables are **not created** by current runtime startup
- Models share `Base` from `backend.models.main_models` (same metadata registry if ever registered together)
- Enums exist in Python but entity columns use plain `String` types

---

## Entity Audits

### Project

| Field | Detail |
|-------|--------|
| **Purpose** | Top-level operational container for graph entities |
| **Architectural responsibility** | Owns WBS templates, location tree, workflow graph, activities, resources, dependencies |
| **Current status** | Schema foundation only — not wired to runtime |

**Relationships (implemented):**

- `1:N` → WbsTemplate, LocationNode, WorkflowNode, WorkflowEdge, ActivityInstance, Resource, Dependency

**Relationships (missing / external):**

- No link to runtime `DailyWorkOrder.project_id` (integer, separate model world)
- No bridge table to MVP project records

**Key fields:** `code`, `title`, `project_type`, `baseline_mode`, `baseline_configuration`, `operational_settings`, `start_at`, `target_finish_at`

**Overlaps:**

- Runtime uses lightweight `project_id` on work orders without `core_operational.Project` row

**Inconsistencies:**

- `ProjectType` enum includes values (`building`, `infrastructure`, etc.) not mirrored in planning prototype project types (`residential_tower`, etc.) — documentation/UX drift, not schema bug

| Assessment | Value |
|------------|-------|
| **Architectural alignment** | **Partial** |
| **Gaps** | No runtime bridge; no global vs project scope policy encoded |
| **Recommendations** | Document adapter strategy in `open-architecture-questions.md` (#5). Do not merge runtime project tables without explicit bridge design. |

---

### WbsTemplate

| Field | Detail |
|-------|--------|
| **Purpose** | Construction activity **type** — reusable taxonomy entry |
| **Architectural responsibility** | Answers **what kind of work** — not when or where it executes |
| **Current status** | Schema foundation only |

**Relationships (implemented):**

- `N:1` → Project
- `1:N` → ActivityInstance

**Relationships (missing per docs):**

- No link to `WorkflowNode` (`core-operational-model.md` states workflow nodes *can be linked to one or more WBS Templates*)
- No reference to global library template ID (canonical `wbs-template-library.md` vs per-project copy)

**Key fields:** `code`, `title`, `category`, `phase`, `repeatable`, `default_duration_days`, `default_resource_hints`

**Overlaps:**

- None with Schedule entity (correct — no Schedule table exists)
- `default_duration_days` could be misread as scheduling; architecturally it is a **default hint** for instantiation (aligned if documented)

**Inconsistencies:**

- **Project-scoped** (`project_id` required) vs **global library** described in `wbs-template-library.md` — open question #3
- No explicit exclusion of capability-layer fields (correct — schema stays construction-native)

| Assessment | Value |
|------------|-------|
| **Architectural alignment** | **Partial** |
| **Gaps** | Missing WorkflowNode↔WbsTemplate association; library scope undefined |
| **Recommendations** | Document seed/copy pattern only. Future junction table or `source_library_code` field is an open design decision — not an audit implementation. |

---

### LocationNode

| Field | Detail |
|-------|--------|
| **Purpose** | Hierarchical execution geography |
| **Architectural responsibility** | Enables location-aware activity instantiation and roll-up |
| **Current status** | Schema foundation only |

**Relationships (implemented):**

- `N:1` → Project
- Self-referential `parent_id` → children tree
- `1:N` → ActivityInstance

**Relationships (missing per docs):**

- No explicit **repeatable cycle** metadata (`location-system.md` — repeatable slab/masonry/MEP cycles)
- No location-specific notes / constraint association fields mentioned in location-system doc
- No BIM / drawing reference fields (future-facing, not required now)

**Key fields:** `node_type`, `code`, `title`, `path`, `level_index`, `sort_order`, `is_active`

**Overlaps:**

- `path` duplicates derivable hierarchy — acceptable denormalization for query performance

**Inconsistencies:**

- `LocationNodeType` enum includes `project`, `block`, `basement`, `area` — richer than planning prototype location types (`tower`, `floor`, `zone`, `room`, `sector`)
- `node_type` stored as `String(40)` — enum not enforced at DB layer

| Assessment | Value |
|------------|-------|
| **Architectural alignment** | **Aligned** |
| **Gaps** | Repeatable cycle pattern not modeled; roll-up logic not in schema (expected — belongs in services later) |
| **Recommendations** | Optional future fields: `cycle_template_id`, `location_notes`. Document as future, not foundation requirement. |

---

### WorkflowNode

| Field | Detail |
|-------|--------|
| **Purpose** | Operational workflow step / node in possibility graph |
| **Architectural responsibility** | Defines **possible** execution meaning — not schedule rows |
| **Current status** | Schema foundation only |

**Relationships (implemented):**

- `N:1` → Project
- `1:N` → WorkflowEdge (incoming/outgoing)
- `1:N` → ActivityInstance (optional `workflow_node_id`)

**Relationships (missing per docs):**

- **No WbsTemplate linkage** despite `core-operational-model.md` explicit statement
- No version / template-set grouping for workflow graphs

**Key fields:** `code`, `title`, `node_type`, `category`, `is_entry_node`, `is_terminal_node`

**Overlaps:**

- Conceptual overlap with WbsTemplate titles (e.g., both may represent "Concrete Pour") — docs allow this but relationship is undocumented in schema

**Inconsistencies:**

- Workflow nodes and WBS templates are parallel taxonomies without formal mapping table

| Assessment | Value |
|------------|-------|
| **Architectural alignment** | **Partial** |
| **Gaps** | Missing WorkflowNode↔WbsTemplate mapping; Workflow Context reduced to optional single FK |
| **Recommendations** | Treat `workflow_node_id` as partial Workflow Context placeholder. Document full context model in open questions. |

---

### WorkflowEdge

| Field | Detail |
|-------|--------|
| **Purpose** | Possible path between workflow nodes (branching graph) |
| **Architectural responsibility** | Encodes **suggestions / possibilities** — not mandatory schedule sequence |
| **Current status** | Schema foundation only |

**Relationships (implemented):**

- `N:1` → Project
- `N:1` → from_node, to_node (WorkflowNode)

**Relationships (missing):**

- No direct link to ActivityInstance path selection history
- No runtime "chosen path" record when PM selects a branch

**Key fields:** `edge_type`, `is_optional`, `condition_expression`, `transition_notes`, `priority_order`

**Overlaps:**

- Distinct from `Dependency` (activity-to-activity) — **correct separation**

**Inconsistencies:**

- `WorkflowEdgeType` enum exists; column is plain string
- `condition_expression` is Text without evaluation spec (acceptable for foundation)

| Assessment | Value |
|------------|-------|
| **Architectural alignment** | **Aligned** |
| **Gaps** | No activity-level path audit trail |
| **Recommendations** | Sufficient for graph representation. Path history is a future behavioral layer. |

---

### ActivityInstance

| Field | Detail |
|-------|--------|
| **Purpose** | **Canonical operational data entity** (per `glossary.md`) |
| **Architectural responsibility** | Executable work unit: WBS type at a location with workflow context |
| **Current status** | Schema foundation only — not runtime entity |

**Relationships (implemented):**

- `N:1` → Project, WbsTemplate, LocationNode, WorkflowNode (optional)
- `1:N` → Dependency (predecessor/successor), Assignment, ProgressLog

**Relationships (missing):**

- No link to `DailyWorkOrder` / `task_id`
- No Constraint / Blocker association
- No state transition history table
- No explicit Workflow Context beyond `workflow_node_id`

**Key fields:** planned/baseline/actual dates, `progress_percent`, `operational_status`, `baseline_locked`

**Overlaps:**

- `progress_percent` on instance vs `ProgressLog.progress_percent` — dual progress representation (risk to Rule 7)
- Date fields support schedule **visualization** but live on executable entity (acceptable — no separate Schedule entity)

**Inconsistencies:**

- `ActivityStatus` enum includes `on_hold`, `cancelled`; planning prototype uses smaller status set
- `operational_status` is string column — enum not enforced
- Planning prototype uses `workflowContext: string`; schema uses optional `workflow_node_id` only — **partial alignment**

| Assessment | Value |
|------------|-------|
| **Architectural alignment** | **Partial** |
| **Gaps** | Workflow Context under-modeled; progress dual-source; no lifecycle transition model at graph level |
| **Recommendations** | Document that `ProgressLog` is operational truth per architecture; instance `progress_percent` should be denormalized snapshot only. Clarify in docs, not code. |

---

### Dependency

| Field | Detail |
|-------|--------|
| **Purpose** | Activity-to-activity execution relationship |
| **Architectural responsibility** | Lightweight FS / SS / FF + lag between **ActivityInstance** rows |
| **Current status** | Schema foundation only |

**Relationships (implemented):**

- `N:1` → Project
- `N:1` → predecessor ActivityInstance, successor ActivityInstance

**Relationships (missing):**

- No cross-project dependencies (correct for scope)
- No soft/hard dependency distinction (`construction-execution-logic-model.md` discusses constraint-like dependency behavior)

**Key fields:** `dependency_type`, `lag_value`, `lag_unit`, `is_active`, `notes`

**Overlaps:**

- None with WorkflowEdge — **correct** (Rule 5)

**Inconsistencies:**

- Enum supports FS, SS, FF only — aligned with lightweight philosophy
- No SF type — consistent with stated scope

| Assessment | Value |
|------------|-------|
| **Architectural alignment** | **Aligned** |
| **Gaps** | No dependency validation rules in schema (expected — engine layer) |
| **Recommendations** | Sufficient for graph dependency representation. |

---

### Resource

| Field | Detail |
|-------|--------|
| **Purpose** | Lightweight operational resource definition |
| **Architectural responsibility** | Manpower / material / equipment — not enterprise HR |
| **Current status** | Schema foundation only |

**Relationships (implemented):**

- `N:1` → Project
- `1:N` → Assignment

**Relationships (missing):**

- No capacity / utilization fields (`construction-execution-logic-model.md` references capacity logic as future)
- No link to workforce extension `Worker` entity

**Key fields:** `resource_type`, `code`, `title`, `unit`, `default_quantity`, `availability_status`

**Overlaps:**

- Workforce extension defines separate worker/crew models — open question #4

**Inconsistencies:**

- `ResourceType` enum vs string column storage

| Assessment | Value |
|------------|-------|
| **Architectural alignment** | **Aligned** |
| **Gaps** | No capacity model; workforce integration undefined |
| **Recommendations** | Keep lightweight by design. Document workforce bridge as optional extension integration. |

---

### Assignment

| Field | Detail |
|-------|--------|
| **Purpose** | Connect Resource to ActivityInstance |
| **Architectural responsibility** | Operational allocation — planned vs actual quantity over time window |
| **Current status** | Schema foundation only |

**Relationships (implemented):**

- `N:1` → ActivityInstance, Resource

**Relationships (missing):**

- No `project_id` ( derivable via activity — acceptable)
- No link to workforce assignment tables

**Key fields:** `planned_quantity`, `actual_quantity`, `allocation_start_at`, `allocation_finish_at`, `assignment_status`

**Overlaps:**

- Name collision with `backend/workforce/` assignment concept — different domain, same word

**Inconsistencies:**

- Simplistic single-resource assignment rows — no multi-crew split modeling (acceptable for foundation)

| Assessment | Value |
|------------|-------|
| **Architectural alignment** | **Partial** |
| **Gaps** | Workforce assignment alignment unresolved; no conflict detection |
| **Recommendations** | Document naming distinction in glossary. Integration spec belongs in open questions. |

---

### ProgressLog

| Field | Detail |
|-------|--------|
| **Purpose** | Operational truth layer for execution feedback |
| **Architectural responsibility** | Captures field progress, resource usage, delays, issues |
| **Current status** | Schema foundation only |

**Relationships (implemented):**

- `N:1` → ActivityInstance

**Relationships (missing):**

- No validation engine cross-reference
- No link to DailyReport rows (runtime truth today)

**Key fields:** `reported_by`, `logged_at`, `progress_percent`, quantities, `delay_hours`, `operational_notes`, `issues`, `status_snapshot`

**Overlaps:**

- Mirrors many `DailyReport` fields conceptually — runtime uses DailyReport, target uses ProgressLog
- Overlaps `ActivityInstance.progress_percent` — truth source ambiguity

**Inconsistencies:**

- Richer than planning prototype progress logs in some fields; planning uses separate delay/comment on activity row

| Assessment | Value |
|------------|-------|
| **Architectural alignment** | **Aligned** |
| **Gaps** | No bridge to DailyReport; dual progress on ActivityInstance |
| **Recommendations** | Document ProgressLog as target truth layer. Instance progress = latest snapshot convention. |

---

## Architectural Rules Verification

### Rule 1 — WBS ≠ Schedule

| Verdict | **Aligned** |
|---------|-------------|
| Evidence | `WbsTemplate` has no dates, predecessors, or sequence order. No Schedule entity exists. WBS phases are taxonomy metadata only. |
| Caveats | `default_duration_days` must remain documented as hint, not schedule. `ActivityInstance` date fields represent executable arrangement, not WBS properties. |
| Risk | Low — developers could misuse WBS ordering in UI as sequence (documentation/discipline issue). |

---

### Rule 2 — Activity Instance is the canonical operational entity

| Verdict | **Aligned** |
|---------|-------------|
| Evidence | `ActivityInstance` is central hub with dependencies, assignments, progress logs. Instantiation schema exists. Glossary confirms canonical status. |
| Caveats | Not wired to runtime. `DailyWorkOrder` remains production entity. |
| Risk | Medium — dual entity worlds until bridge exists. |

---

### Rule 3 — Operational Task is UX terminology only

| Verdict | **Aligned** |
|---------|-------------|
| Evidence | No `OperationalTask` table in `core_operational`. Schema uses `ActivityInstance` only. |
| Caveats | `architectural-separation-model.md` still says "Operational Task Nodes" — documentation terminology drift outside this package. |
| Risk | Low for schema; medium for doc confusion. |

---

### Rule 4 — Location-aware execution is supported

| Verdict | **Aligned** |
|---------|-------------|
| Evidence | `LocationNode` hierarchy with `parent_id`, `path`, `level_index`. `ActivityInstance.location_node_id` is required. |
| Caveats | Repeatable location cycles not encoded. Roll-up analytics not in schema. |
| Risk | Low for foundation; medium for advanced location patterns. |

---

### Rule 5 — Workflow and Dependency are separate concepts

| Verdict | **Aligned** |
|---------|-------------|
| Evidence | `WorkflowNode`/`WorkflowEdge` model possibility graph. `Dependency` models activity-instance coordination (FS/SS/FF). |
| Caveats | Without WorkflowNode↔WbsTemplate mapping, workflow suggestions may duplicate WBS titles informally. |
| Risk | Low — separation is structurally correct. |

---

### Rule 6 — Operational Capabilities are not embedded inside WBS

| Verdict | **Aligned** |
|---------|-------------|
| Evidence | `WbsTemplate` fields are construction taxonomy only (phase, category, resource hints). No analytics/KPI/automation fields. |
| Caveats | WBS documentation reconciliation removed capability items from catalog; schema never included them. |
| Risk | Low. |

---

### Rule 7 — Schedule is visualization, not operational truth

| Verdict | **Partial** |
|---------|-------------|
| Evidence | No Schedule table. Gantt/schedule views derive from activity dates + dependencies per philosophy docs. `ProgressLog` designed as truth layer. |
| Caveats | `ActivityInstance.progress_percent` coexists with `ProgressLog.progress_percent` without documented precedence rule in schema. Planned dates stored on activity blur "truth" vs "view" if treated as authoritative progress. |
| Risk | Medium — requires documented convention: logs = truth, dates = arrangement, instance progress = snapshot. |

---

### Rule 8 — Graph-based execution can be represented by current schema

| Verdict | **Partial** |
|---------|-------------|
| Evidence | Workflow graph (nodes + edges), activity instances, activity dependencies, location tree, resource assignments — sufficient for static graph representation. |
| Caveats | Missing: Constraint entity, Workflow Context formal model, WorkflowNode↔WbsTemplate mapping, path selection history, graph mutation audit, event entity. |
| Risk | Medium — representable but incomplete for full execution logic model in docs. |

---

## Architectural Gaps (Documentation Only)

These gaps are **identified only**. No implementation is requested by this audit.

### Missing Entities

| Gap | Current state | Architecture reference |
|-----|---------------|------------------------|
| **Constraint** | Not in schema. Runtime has lifecycle blockers on work orders only. | `construction-execution-logic-model.md`, `glossary.md`, open question #1 |
| **Event** | Not modeled | `reviews/execution-logic-architecture-review.md` Layer 3 |
| **Schedule View** | Not an entity (correct) — but no view metadata or snapshot model | `scheduling-philosophy.md` |
| **Operational Task** | Correctly absent as entity | `glossary.md` |

### Under-Defined Concepts

| Gap | Detail |
|-----|--------|
| **Workflow Context** | Formula uses three inputs; schema only has optional `workflow_node_id`. Planning prototype uses free-text `workflowContext` string. |
| **WorkflowNode ↔ WbsTemplate** | Documented relationship; no junction or FK in schema. |
| **WBS library scope** | `WbsTemplate.project_id` implies project ownership; global library is documentation-only today. |
| **Activity state model** | `operational_status` string + `ActivityStatus` enum not enforced. No transition table at graph level (lifecycle exists separately for work orders). |
| **Progress truth precedence** | ActivityInstance.progress_percent vs ProgressLog vs future DailyReport bridge undefined in schema docs. |

### Simplifications (Acceptable for Foundation)

| Area | Assessment |
|------|------------|
| Resource capacity | Not modeled — future layer |
| Assignment conflict detection | Not modeled — future layer |
| Graph mutation / split / merge | Not modeled — future layer |
| Dependency hard/soft types | Not modeled — acceptable |
| Enum DB enforcement | Enums in Python; columns are strings — validation deferred to application layer |

### Schema ↔ Runtime Gaps

| Gap | Detail |
|-----|--------|
| Not registered in `api.py` | Tables never created in production startup |
| Shared `Base` with runtime models | Potential metadata coupling if registered without migration plan |
| No FK bridge to `daily_work_orders` | Runtime and graph are isolated worlds |
| `ProgressLog` vs `DailyReport` | Parallel truth models |

### Schema ↔ Planning Prototype Gaps

| core_operational | Planning prototype | Gap |
|------------------|-------------------|-----|
| Integer IDs | String IDs | Expected for prototype |
| WorkflowNode / WorkflowEdge | Not modeled — suggestion map only | Partial |
| `workflow_node_id` | `workflowContext: string` | Misaligned |
| Full ActivityStatus enum | 6 statuses | Partial |
| ProjectType enum | Different project type union | Partial |

---

## Cross-Entity Relationship Map (As Implemented)

```
Project
 ├── WbsTemplate ──────────────┐
 ├── LocationNode ─────────────┤
 ├── WorkflowNode ◄── WorkflowEdge
 ├── Resource                  │
 ├── ActivityInstance ◄────────┘ (wbs + location + optional workflow_node)
 │    ├── Dependency (activity ↔ activity)
 │    ├── Assignment → Resource
 │    └── ProgressLog
 └── Dependency (also project-scoped)
```

**Not implemented in schema (documented in architecture):**

```
WorkflowNode ──?── WbsTemplate     (documented, missing)
ActivityInstance ──?── DailyWorkOrder (runtime bridge, missing)
ActivityInstance ──?── Constraint    (missing)
```

---

## Architecture Readiness Assessment

### Operational Graph Readiness — **Medium**

**Why not High:**

- Core entities and activity-level dependencies exist
- Workflow branching structure exists
- Missing Constraint, Workflow Context formalization, WorkflowNode↔WbsTemplate link
- Not registered or deployed

**Why not Low:**

- Entity design matches graph philosophy
- Relationship map is coherent
- Optional/conditional workflow edges support branching

---

### Planning Prototype Alignment — **Medium**

**Why not High:**

- Prototype mirrors WBS + Location + Activity + Dependency + Resource concepts
- Workflow suggestions align with workflow-graph philosophy
- Different ID types, no WorkflowNode entities, string Workflow Context

**Why not Low:**

- Instantiation formula is recognizably the same
- Phase-grouped WBS aligns with `wbs-template-library.md`

---

### Runtime Compatibility — **Low**

**Why:**

- `core_operational` is not imported, migrated, or exposed via API
- Production truth flows through DailyWorkOrder / DailyReport
- No documented adapter or FK bridge
- Lifecycle and validation engines operate on work orders, not ActivityInstance

**Note:** Low runtime compatibility is **expected** at foundation stage — not a schema defect.

---

### Future Extensibility — **High**

**Why:**

- JSON fields (`baseline_configuration`, `operational_settings`, `default_resource_hints`)
- Optional workflow association — supports incremental Workflow Context evolution
- `condition_expression` on edges — future conditional routing
- Separate packages — clean boundary from MVP
- Lightweight entities — room to add junction tables without breaking core shapes

---

## Summary of Findings

1. **`backend/core_operational/` correctly implements the 10-entity foundation** described in architecture docs.
2. **Strongest alignment:** WBS≠Schedule, Activity Instance centrality, Workflow vs Dependency separation, location-aware instantiation, capability-free WBS schema.
3. **Primary misalignments:** missing Constraint entity, undefined Workflow Context (only partial FK), missing WorkflowNode↔WbsTemplate relationship, WBS global library vs project-scoped templates.
4. **Runtime is intentionally disconnected** — foundation audit confirms schema-only status.
5. **Enum vocabulary exists but is not enforced** at the database column level — Partial implementation discipline.
6. **Progress truth needs explicit convention** between ActivityInstance snapshot and ProgressLog entries.

---

## Architectural Strengths

- Clear separation of taxonomy (WBS), geography (Location), possibility graph (Workflow), execution (Activity), coordination (Dependency), resources, and truth (ProgressLog)
- No Schedule entity — avoids WBS→Gantt collapse
- No Operational Task entity — preserves glossary distinction
- WorkflowEdge optional/conditional fields support non-linear construction paths
- Package boundary is clean and documented
- Pydantic schemas and instantiation schema ready for future API adoption
- Conceptual relationship map matches entity models closely

---

## Architectural Risks

| Risk | Severity | Mitigation (documentation) |
|------|----------|----------------------------|
| Assumption that graph is live because schema exists | High | `current-vs-target-architecture.md` — keep visible |
| Dual entity worlds (Work Order vs Activity Instance) | High | Bridge open question — do not merge without design |
| Workflow Context ambiguity | Medium | Formalize in open questions before API work |
| Progress dual-source confusion | Medium | Document ProgressLog as truth; instance field as snapshot |
| WorkflowNode/WbsTemplate drift | Medium | Add junction spec to future docs when decided |
| Shared SQLAlchemy Base with runtime | Medium | Migration plan doc before registration |
| String columns vs enums | Low | Application validation when APIs are added |

---

## Missing Concepts (Not in Schema)

Document only — no implementation recommended in this audit:

1. Constraint entity (or explicit lifecycle-blocker mapping policy)
2. Workflow Context entity or composite model
3. WorkflowNode ↔ WbsTemplate association
4. Activity state transition history (graph-level)
5. Event entity
6. Graph mutation / path selection audit
7. Runtime bridge: DailyWorkOrder ↔ ActivityInstance
8. DailyReport ↔ ProgressLog mapping
9. Resource capacity model
10. Global WBS library registry vs project template copy mechanism

---

## Recommended Next Documentation Step

**Do not implement code next.** Recommended documentation sequence:

1. **`docs/architecture/bridges/runtime-to-operational-graph-bridge.md`** (new)
   - Define options for Work Order ↔ Activity Instance relationship
   - Define ProgressLog ↔ DailyReport mapping philosophy
   - Status: Proposed documentation only

2. **Update `open-architecture-questions.md`**
   - Add findings: WorkflowNode↔WbsTemplate, progress truth precedence
   - Link to this audit

3. **Update `backend/core_operational/docs/README.md`**
   - Add alignment status labels per entity
   - Link to this audit as canonical foundation reference

4. **Terminology cleanup pass**
   - Replace remaining "Operational Task Node" in `architectural-separation-model.md` with glossary references

5. **Defer until bridge doc exists**
   - Rewrite `backend-architecture.md` / `database-architecture.md` with both runtime tables and `core_operational_*` tables side by side

---

## Audit Conclusion

`backend/core_operational/` is **fit for purpose as a schema foundation** and is **Partially to Aligned** with BetavanX architecture documentation. It is **not** misaligned in direction — gaps are primarily **missing relationships**, **under-specified Workflow Context**, **absent Constraint model**, and **intentional runtime disconnect**.

The foundation supports future Operational Graph work without requiring entity redesign. Next work should be **documentation of bridges and open questions**, not feature expansion or runtime wiring — unless explicitly scoped in a separate engineering task.

---

**Audit artifacts:**

| Artifact | Path |
|----------|------|
| This audit | `docs/architecture/audits/core-operational-foundation-audit.md` |
| Layer context | `docs/architecture/current-vs-target-architecture.md` |
| Terminology | `docs/architecture/glossary.md` |
| Open questions | `docs/architecture/open-architecture-questions.md` |
