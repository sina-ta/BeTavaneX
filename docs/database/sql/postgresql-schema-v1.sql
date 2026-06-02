-- BetavanX Phase 1 PostgreSQL Schema
-- Source: docs/database/data-dictionary.md, erd.md, entity-catalog.md,
--         relationship-matrix.md, boq-mapping-specification.md
-- Target: PostgreSQL 14+
-- Idempotent: DROP + CREATE (destructive reset)

BEGIN;

-- ---------------------------------------------------------------------------
-- Drop tables (dependency order)
-- ---------------------------------------------------------------------------

DROP TABLE IF EXISTS boq_mappings CASCADE;
DROP TABLE IF EXISTS blockers CASCADE;
DROP TABLE IF EXISTS approvals CASCADE;
DROP TABLE IF EXISTS punch_items CASCADE;
DROP TABLE IF EXISTS inspections CASCADE;
DROP TABLE IF EXISTS daily_reports CASCADE;
DROP TABLE IF EXISTS work_order_workflow_steps CASCADE;
DROP TABLE IF EXISTS work_orders CASCADE;
DROP TABLE IF EXISTS workflow_steps CASCADE;
DROP TABLE IF EXISTS activity_instances CASCADE;
DROP TABLE IF EXISTS boq_items CASCADE;
DROP TABLE IF EXISTS workflow_step_templates CASCADE;
DROP TABLE IF EXISTS locations CASCADE;
DROP TABLE IF EXISTS wbs_items CASCADE;
DROP TABLE IF EXISTS projects CASCADE;

-- ---------------------------------------------------------------------------
-- Planning Layer
-- ---------------------------------------------------------------------------

CREATE TABLE projects (
    id              UUID          NOT NULL DEFAULT gen_random_uuid(),
    code            VARCHAR(100)  NOT NULL,
    name            VARCHAR(255)  NOT NULL,
    description     TEXT,
    status          VARCHAR(50)   NOT NULL DEFAULT 'ACTIVE',
    planned_start   DATE,
    planned_finish  DATE,
    created_at      TIMESTAMPTZ   NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMPTZ   NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT projects_pkey PRIMARY KEY (id),
    CONSTRAINT projects_code_key UNIQUE (code),
    CONSTRAINT projects_status_check CHECK (
        status IN ('DRAFT', 'ACTIVE', 'ON_HOLD', 'COMPLETED', 'CANCELLED')
    )
);

COMMENT ON TABLE projects IS 'Planning Layer: top-level project container.';
COMMENT ON COLUMN projects.status IS 'Allowed: DRAFT, ACTIVE, ON_HOLD, COMPLETED, CANCELLED.';

CREATE INDEX idx_projects_status ON projects (status);


CREATE TABLE wbs_items (
    id              UUID          NOT NULL DEFAULT gen_random_uuid(),
    project_id      UUID          NOT NULL,
    parent_id       UUID,
    code            VARCHAR(100)  NOT NULL,
    name            VARCHAR(255)  NOT NULL,
    description     TEXT,
    level           INTEGER       NOT NULL,
    status          VARCHAR(50)   NOT NULL DEFAULT 'ACTIVE',
    created_at      TIMESTAMPTZ   NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMPTZ   NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT wbs_items_pkey PRIMARY KEY (id),
    CONSTRAINT wbs_items_project_id_fkey FOREIGN KEY (project_id)
        REFERENCES projects (id) ON DELETE RESTRICT,
    CONSTRAINT wbs_items_parent_id_fkey FOREIGN KEY (parent_id)
        REFERENCES wbs_items (id) ON DELETE SET NULL,
    CONSTRAINT wbs_items_project_id_code_key UNIQUE (project_id, code),
    CONSTRAINT wbs_items_status_check CHECK (
        status IN ('ACTIVE', 'COMPLETED', 'CANCELLED')
    )
);

COMMENT ON TABLE wbs_items IS 'Planning Layer: project work breakdown structure (hierarchical).';

CREATE INDEX idx_wbs_items_project_id ON wbs_items (project_id);
CREATE INDEX idx_wbs_items_parent_id ON wbs_items (parent_id);


CREATE TABLE locations (
    id              UUID          NOT NULL DEFAULT gen_random_uuid(),
    project_id      UUID          NOT NULL,
    parent_id       UUID,
    code            VARCHAR(100)  NOT NULL,
    name            VARCHAR(255)  NOT NULL,
    description     TEXT,
    level           INTEGER       NOT NULL,
    status          VARCHAR(50)   NOT NULL DEFAULT 'ACTIVE',
    created_at      TIMESTAMPTZ   NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMPTZ   NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT locations_pkey PRIMARY KEY (id),
    CONSTRAINT locations_project_id_fkey FOREIGN KEY (project_id)
        REFERENCES projects (id) ON DELETE RESTRICT,
    CONSTRAINT locations_parent_id_fkey FOREIGN KEY (parent_id)
        REFERENCES locations (id) ON DELETE SET NULL,
    CONSTRAINT locations_project_id_code_key UNIQUE (project_id, code),
    CONSTRAINT locations_status_check CHECK (
        status IN ('ACTIVE', 'CLOSED')
    )
);

COMMENT ON TABLE locations IS 'Planning Layer: project location hierarchy.';

CREATE INDEX idx_locations_project_id ON locations (project_id);
CREATE INDEX idx_locations_parent_id ON locations (parent_id);


CREATE TABLE boq_items (
    id              UUID           NOT NULL DEFAULT gen_random_uuid(),
    project_id      UUID           NOT NULL,
    item_number     VARCHAR(100)   NOT NULL,
    item_code       VARCHAR(100),
    title           VARCHAR(255)   NOT NULL,
    description     TEXT,
    unit            VARCHAR(50)    NOT NULL,
    quantity        NUMERIC(18, 3) NOT NULL,
    rate            NUMERIC(18, 2) NOT NULL,
    planned_cost    NUMERIC(18, 2) NOT NULL,
    currency        VARCHAR(10)    NOT NULL DEFAULT 'IRR',
    status          VARCHAR(50)    NOT NULL DEFAULT 'ACTIVE',
    created_at      TIMESTAMPTZ    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMPTZ    NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT boq_items_pkey PRIMARY KEY (id),
    CONSTRAINT boq_items_project_id_fkey FOREIGN KEY (project_id)
        REFERENCES projects (id) ON DELETE RESTRICT,
    CONSTRAINT boq_items_quantity_positive_check CHECK (quantity > 0),
    CONSTRAINT boq_items_rate_non_negative_check CHECK (rate >= 0),
    CONSTRAINT boq_items_status_check CHECK (
        status IN ('DRAFT', 'APPROVED', 'ACTIVE', 'CLOSED')
    )
);

COMMENT ON TABLE boq_items IS 'Financial Layer: bill of quantity items (financial measurement reality).';
COMMENT ON COLUMN boq_items.planned_cost IS 'Must equal quantity * rate.';

CREATE INDEX idx_boq_items_project_id ON boq_items (project_id);


-- ---------------------------------------------------------------------------
-- Execution Knowledge Layer
-- ---------------------------------------------------------------------------

CREATE TABLE workflow_step_templates (
    id                    UUID          NOT NULL DEFAULT gen_random_uuid(),
    code                  VARCHAR(100)  NOT NULL,
    name                  VARCHAR(255)  NOT NULL,
    description           TEXT,
    method_statement      TEXT,
    safety_requirements   TEXT,
    inspection_checklist  TEXT,
    required_resources    JSONB,
    required_permits      JSONB,
    required_documents    JSONB,
    execution_guide       TEXT,
    standard_references   TEXT,
    status                VARCHAR(50)   NOT NULL DEFAULT 'ACTIVE',
    created_at            TIMESTAMPTZ   NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at            TIMESTAMPTZ   NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT workflow_step_templates_pkey PRIMARY KEY (id),
    CONSTRAINT workflow_step_templates_code_key UNIQUE (code),
    CONSTRAINT workflow_step_templates_status_check CHECK (
        status IN ('ACTIVE', 'ARCHIVED')
    )
);

COMMENT ON TABLE workflow_step_templates IS
    'Execution Knowledge Layer: reusable templates; WorkflowSteps are snapshot instances.';
COMMENT ON COLUMN workflow_step_templates.required_resources IS 'JSONB snapshot of resource requirements.';

CREATE INDEX idx_workflow_step_templates_status ON workflow_step_templates (status);


-- ---------------------------------------------------------------------------
-- Construction Reality Layer
-- ---------------------------------------------------------------------------

CREATE TABLE activity_instances (
    id                    UUID          NOT NULL DEFAULT gen_random_uuid(),
    project_id            UUID          NOT NULL,
    wbs_item_id           UUID          NOT NULL,
    location_id           UUID          NOT NULL,
    code                  VARCHAR(100)  NOT NULL,
    name                  VARCHAR(255)  NOT NULL,
    planned_start         DATE,
    planned_finish        DATE,
    planned_duration_days INTEGER,
    status                VARCHAR(50)   NOT NULL DEFAULT 'ACTIVE',
    created_at            TIMESTAMPTZ   NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at            TIMESTAMPTZ   NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT activity_instances_pkey PRIMARY KEY (id),
    CONSTRAINT activity_instances_project_id_fkey FOREIGN KEY (project_id)
        REFERENCES projects (id) ON DELETE RESTRICT,
    CONSTRAINT activity_instances_wbs_item_id_fkey FOREIGN KEY (wbs_item_id)
        REFERENCES wbs_items (id) ON DELETE RESTRICT,
    CONSTRAINT activity_instances_location_id_fkey FOREIGN KEY (location_id)
        REFERENCES locations (id) ON DELETE RESTRICT,
    CONSTRAINT activity_instances_project_id_code_key UNIQUE (project_id, code),
    CONSTRAINT activity_instances_project_wbs_location_key
        UNIQUE (project_id, wbs_item_id, location_id),
    CONSTRAINT activity_instances_status_check CHECK (
        status IN ('ACTIVE', 'COMPLETED', 'CANCELLED')
    )
);

COMMENT ON TABLE activity_instances IS
    'Construction Reality: WBS Item x Location planning commitment.';
COMMENT ON COLUMN activity_instances.status IS
    'Lifecycle: ACTIVE, COMPLETED, CANCELLED. READY is not a status (see workflow_steps.ready).';

CREATE INDEX idx_activity_instances_project_id ON activity_instances (project_id);
CREATE INDEX idx_activity_instances_wbs_item_id ON activity_instances (wbs_item_id);
CREATE INDEX idx_activity_instances_location_id ON activity_instances (location_id);
CREATE INDEX idx_activity_instances_status ON activity_instances (status);


-- ---------------------------------------------------------------------------
-- Execution Reality Layer
-- ---------------------------------------------------------------------------

CREATE TABLE workflow_steps (
    id                    UUID           NOT NULL DEFAULT gen_random_uuid(),
    activity_instance_id  UUID           NOT NULL,
    workflow_template_id  UUID,
    code                  VARCHAR(100)   NOT NULL,
    name                  VARCHAR(255)   NOT NULL,
    status                VARCHAR(50)    NOT NULL,
    ready                 BOOLEAN        NOT NULL DEFAULT FALSE,
    progress_percent      NUMERIC(5, 2)  NOT NULL DEFAULT 0,
    planned_weight        NUMERIC(8, 2),
    planned_start         DATE,
    planned_finish        DATE,
    actual_start          DATE,
    actual_finish         DATE,
    created_at            TIMESTAMPTZ    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at            TIMESTAMPTZ    NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT workflow_steps_pkey PRIMARY KEY (id),
    CONSTRAINT workflow_steps_activity_instance_id_fkey FOREIGN KEY (activity_instance_id)
        REFERENCES activity_instances (id) ON DELETE RESTRICT,
    CONSTRAINT workflow_steps_workflow_template_id_fkey FOREIGN KEY (workflow_template_id)
        REFERENCES workflow_step_templates (id) ON DELETE RESTRICT,
    CONSTRAINT workflow_steps_activity_instance_id_code_key
        UNIQUE (activity_instance_id, code),
    CONSTRAINT workflow_steps_status_check CHECK (
        status IN (
            'PLANNED',
            'IN_PROGRESS',
            'COMPLETED',
            'INSPECTION_PENDING',
            'INSPECTION_FAILED',
            'REWORK_REQUIRED',
            'APPROVED'
        )
    ),
    CONSTRAINT workflow_steps_progress_percent_range_check CHECK (
        progress_percent >= 0 AND progress_percent <= 100
    ),
    CONSTRAINT workflow_steps_planned_weight_range_check CHECK (
        planned_weight IS NULL OR (planned_weight >= 0 AND planned_weight <= 100)
    )
);

COMMENT ON TABLE workflow_steps IS
    'Execution Reality: primary operational entity; owns progress.';
COMMENT ON COLUMN workflow_steps.ready IS
    'Computed readiness condition. READY is not a lifecycle status.';
COMMENT ON COLUMN workflow_steps.progress_percent IS
    'Derived from completed WorkOrder weights (commitment-based progress).';
COMMENT ON COLUMN workflow_steps.planned_weight IS
    'Relative weight for ActivityInstance progress rollup.';
-- earned_value is derived, not persisted: Workflow Progress x Planned Cost

CREATE INDEX idx_workflow_steps_activity_instance_id ON workflow_steps (activity_instance_id);
CREATE INDEX idx_workflow_steps_workflow_template_id ON workflow_steps (workflow_template_id);
CREATE INDEX idx_workflow_steps_status ON workflow_steps (status);


-- ---------------------------------------------------------------------------
-- Execution Coordination Layer
-- ---------------------------------------------------------------------------

CREATE TABLE work_orders (
    id                UUID          NOT NULL DEFAULT gen_random_uuid(),
    project_id        UUID          NOT NULL,
    work_order_number VARCHAR(100)  NOT NULL,
    title             VARCHAR(255)  NOT NULL,
    description       TEXT,
    planned_date      DATE          NOT NULL,
    status            VARCHAR(50)   NOT NULL DEFAULT 'CREATED',
    created_by        UUID,
    created_at        TIMESTAMPTZ   NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at        TIMESTAMPTZ   NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT work_orders_pkey PRIMARY KEY (id),
    CONSTRAINT work_orders_project_id_fkey FOREIGN KEY (project_id)
        REFERENCES projects (id) ON DELETE RESTRICT,
    CONSTRAINT work_orders_project_id_work_order_number_key
        UNIQUE (project_id, work_order_number),
    CONSTRAINT work_orders_status_check CHECK (
        status IN ('CREATED', 'ASSIGNED', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED')
    )
);

COMMENT ON TABLE work_orders IS
    'Execution Coordination: daily execution slice; not operational truth.';
COMMENT ON COLUMN work_orders.created_by IS
    'Phase 1: user UUID reference only; no users table or FK enforcement.';

CREATE INDEX idx_work_orders_project_id ON work_orders (project_id);
CREATE INDEX idx_work_orders_planned_date ON work_orders (planned_date);
CREATE INDEX idx_work_orders_status ON work_orders (status);


CREATE TABLE work_order_workflow_steps (
    id               UUID          NOT NULL DEFAULT gen_random_uuid(),
    work_order_id    UUID          NOT NULL,
    workflow_step_id UUID          NOT NULL,
    execution_weight NUMERIC(8, 2) NOT NULL,
    created_at       TIMESTAMPTZ   NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT work_order_workflow_steps_pkey PRIMARY KEY (id),
    CONSTRAINT work_order_workflow_steps_work_order_id_fkey FOREIGN KEY (work_order_id)
        REFERENCES work_orders (id) ON DELETE CASCADE,
    CONSTRAINT work_order_workflow_steps_workflow_step_id_fkey FOREIGN KEY (workflow_step_id)
        REFERENCES workflow_steps (id) ON DELETE CASCADE,
    CONSTRAINT work_order_workflow_steps_work_order_step_key
        UNIQUE (work_order_id, workflow_step_id),
    CONSTRAINT work_order_workflow_steps_execution_weight_positive_check CHECK (
        execution_weight > 0 AND execution_weight <= 100
    )
);

COMMENT ON TABLE work_order_workflow_steps IS
    'Junction: WorkflowStep N:N WorkOrder; execution_weight drives step progress.';
COMMENT ON COLUMN work_order_workflow_steps.execution_weight IS
    'Contribution of this WorkOrder toward WorkflowStep completion (percent).';

CREATE INDEX idx_work_order_workflow_steps_work_order_id
    ON work_order_workflow_steps (work_order_id);
CREATE INDEX idx_work_order_workflow_steps_workflow_step_id
    ON work_order_workflow_steps (workflow_step_id);


-- ---------------------------------------------------------------------------
-- Execution Evidence Layer
-- ---------------------------------------------------------------------------

CREATE TABLE daily_reports (
    id                       UUID          NOT NULL DEFAULT gen_random_uuid(),
    work_order_id            UUID          NOT NULL,
    report_date              DATE          NOT NULL,
    status                   VARCHAR(50)   NOT NULL DEFAULT 'DRAFT',
    summary                  TEXT,
    execution_notes          TEXT,
    issue_notes              TEXT,
    delay_notes              TEXT,
    weather_notes            TEXT,
    evidence_metadata        JSONB,
    submitted_by             UUID,
    submitted_at             TIMESTAMPTZ,
    reported_manpower        INTEGER       DEFAULT 0,
    reported_equipment       INTEGER       DEFAULT 0,
    reported_material_entries INTEGER      DEFAULT 0,
    created_at               TIMESTAMPTZ   NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at               TIMESTAMPTZ   NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT daily_reports_pkey PRIMARY KEY (id),
    CONSTRAINT daily_reports_work_order_id_fkey FOREIGN KEY (work_order_id)
        REFERENCES work_orders (id) ON DELETE RESTRICT,
    CONSTRAINT daily_reports_status_check CHECK (
        status IN ('DRAFT', 'SUBMITTED', 'REVIEWED', 'ACCEPTED', 'REJECTED')
    )
);

COMMENT ON TABLE daily_reports IS
    'Execution Evidence: field observations; does not own progress.';
COMMENT ON COLUMN daily_reports.evidence_metadata IS
    'JSONB: photos, attachments, documents, observations.';
COMMENT ON COLUMN daily_reports.submitted_by IS
    'Phase 1: user UUID reference only; no users table or FK enforcement.';

CREATE INDEX idx_daily_reports_work_order_id ON daily_reports (work_order_id);
CREATE INDEX idx_daily_reports_report_date ON daily_reports (report_date);
CREATE INDEX idx_daily_reports_status ON daily_reports (status);


-- ---------------------------------------------------------------------------
-- Quality Layer
-- ---------------------------------------------------------------------------

CREATE TABLE inspections (
    id                UUID          NOT NULL DEFAULT gen_random_uuid(),
    workflow_step_id  UUID          NOT NULL,
    inspection_type   VARCHAR(100)  NOT NULL,
    inspection_date   DATE          NOT NULL,
    status            VARCHAR(50)   NOT NULL,
    inspector_name    VARCHAR(255),
    inspection_notes  TEXT,
    result            VARCHAR(50)   NOT NULL,
    created_at        TIMESTAMPTZ   NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at        TIMESTAMPTZ   NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT inspections_pkey PRIMARY KEY (id),
    CONSTRAINT inspections_workflow_step_id_fkey FOREIGN KEY (workflow_step_id)
        REFERENCES workflow_steps (id) ON DELETE RESTRICT,
    CONSTRAINT inspections_status_check CHECK (
        status IN ('CREATED', 'SCHEDULED', 'IN_PROGRESS', 'PASSED', 'FAILED')
    ),
    CONSTRAINT inspections_result_check CHECK (
        result IN ('PASS', 'FAIL')
    )
);

COMMENT ON TABLE inspections IS 'Quality Verification: belongs to WorkflowStep.';

CREATE INDEX idx_inspections_workflow_step_id ON inspections (workflow_step_id);
CREATE INDEX idx_inspections_inspection_date ON inspections (inspection_date);


CREATE TABLE punch_items (
    id                UUID          NOT NULL DEFAULT gen_random_uuid(),
    workflow_step_id  UUID          NOT NULL,
    inspection_id     UUID          NOT NULL,
    title             VARCHAR(255)  NOT NULL,
    description       TEXT,
    severity          VARCHAR(50)   NOT NULL,
    status            VARCHAR(50)   NOT NULL,
    assigned_to       UUID,
    due_date          DATE,
    resolution_notes  TEXT,
    closed_at         TIMESTAMPTZ,
    created_at        TIMESTAMPTZ   NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at        TIMESTAMPTZ   NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT punch_items_pkey PRIMARY KEY (id),
    CONSTRAINT punch_items_workflow_step_id_fkey FOREIGN KEY (workflow_step_id)
        REFERENCES workflow_steps (id) ON DELETE RESTRICT,
    CONSTRAINT punch_items_inspection_id_fkey FOREIGN KEY (inspection_id)
        REFERENCES inspections (id) ON DELETE RESTRICT,
    CONSTRAINT punch_items_severity_check CHECK (
        severity IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')
    ),
    CONSTRAINT punch_items_status_check CHECK (
        status IN (
            'OPEN',
            'ASSIGNED',
            'IN_PROGRESS',
            'RESOLVED',
            'VERIFIED',
            'CLOSED',
            'REOPENED'
        )
    )
);

COMMENT ON TABLE punch_items IS 'Quality Findings: originated from Inspection; may block Approval at app level.';
COMMENT ON COLUMN punch_items.assigned_to IS
    'Phase 1: user UUID reference only; no users table or FK enforcement.';

CREATE INDEX idx_punch_items_workflow_step_id ON punch_items (workflow_step_id);
CREATE INDEX idx_punch_items_inspection_id ON punch_items (inspection_id);
CREATE INDEX idx_punch_items_status ON punch_items (status);


CREATE TABLE approvals (
    id                UUID          NOT NULL DEFAULT gen_random_uuid(),
    workflow_step_id  UUID          NOT NULL,
    approval_type     VARCHAR(100)  NOT NULL DEFAULT 'FINAL',
    status            VARCHAR(50)   NOT NULL,
    approval_date     DATE,
    approved_by       UUID,
    approval_notes    TEXT,
    rejection_reason  TEXT,
    created_at        TIMESTAMPTZ   NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at        TIMESTAMPTZ   NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT approvals_pkey PRIMARY KEY (id),
    CONSTRAINT approvals_workflow_step_id_fkey FOREIGN KEY (workflow_step_id)
        REFERENCES workflow_steps (id) ON DELETE RESTRICT,
    CONSTRAINT approvals_status_check CHECK (
        status IN ('PENDING', 'UNDER_REVIEW', 'APPROVED', 'REJECTED')
    )
);

COMMENT ON TABLE approvals IS
    'Operational Approval: FK to WorkflowStep only; depends on Inspection/PunchItem outcomes at application level.';
COMMENT ON COLUMN approvals.approved_by IS
    'Phase 1: user UUID reference only; no users table or FK enforcement.';

CREATE INDEX idx_approvals_workflow_step_id ON approvals (workflow_step_id);
CREATE INDEX idx_approvals_status ON approvals (status);


-- ---------------------------------------------------------------------------
-- Operational Constraint Layer
-- ---------------------------------------------------------------------------

CREATE TABLE blockers (
    id                UUID          NOT NULL DEFAULT gen_random_uuid(),
    workflow_step_id  UUID          NOT NULL,
    title             VARCHAR(255)  NOT NULL,
    description       TEXT,
    blocker_type      VARCHAR(100)  NOT NULL,
    severity          VARCHAR(50)   NOT NULL,
    status            VARCHAR(50)   NOT NULL,
    detected_date     DATE          NOT NULL,
    resolved_date     DATE,
    reported_by       UUID,
    root_cause        TEXT,
    resolution_notes  TEXT,
    created_at        TIMESTAMPTZ   NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at        TIMESTAMPTZ   NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT blockers_pkey PRIMARY KEY (id),
    CONSTRAINT blockers_workflow_step_id_fkey FOREIGN KEY (workflow_step_id)
        REFERENCES workflow_steps (id) ON DELETE RESTRICT,
    CONSTRAINT blockers_blocker_type_check CHECK (
        blocker_type IN (
            'WEATHER',
            'EQUIPMENT',
            'MATERIAL',
            'WORKFORCE',
            'SITE_CONDITION',
            'EXTERNAL'
        )
    ),
    CONSTRAINT blockers_severity_check CHECK (
        severity IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')
    ),
    CONSTRAINT blockers_status_check CHECK (
        status IN (
            'OPEN',
            'ACKNOWLEDGED',
            'MITIGATION_IN_PROGRESS',
            'RESOLVED',
            'CLOSED',
            'REOPENED'
        )
    )
);

COMMENT ON TABLE blockers IS
    'Operational Constraints: unexpected interruption; distinct from ready (not ready).';
COMMENT ON COLUMN blockers.reported_by IS
    'Phase 1: user UUID reference only; no users table or FK enforcement.';

CREATE INDEX idx_blockers_workflow_step_id ON blockers (workflow_step_id);
CREATE INDEX idx_blockers_status ON blockers (status);
CREATE INDEX idx_blockers_detected_date ON blockers (detected_date);


-- ---------------------------------------------------------------------------
-- Financial Integration Layer
-- ---------------------------------------------------------------------------

CREATE TABLE boq_mappings (
    id                  UUID           NOT NULL DEFAULT gen_random_uuid(),
    workflow_step_id    UUID           NOT NULL,
    boq_item_id          UUID           NOT NULL,
    allocated_quantity  NUMERIC(18, 3) NOT NULL,
    allocated_cost      NUMERIC(18, 2) NOT NULL,
    allocation_percentage NUMERIC(6, 2),
    notes               TEXT,
    created_at          TIMESTAMPTZ    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMPTZ    NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT boq_mappings_pkey PRIMARY KEY (id),
    CONSTRAINT boq_mappings_workflow_step_id_fkey FOREIGN KEY (workflow_step_id)
        REFERENCES workflow_steps (id) ON DELETE RESTRICT,
    CONSTRAINT boq_mappings_boq_item_id_fkey FOREIGN KEY (boq_item_id)
        REFERENCES boq_items (id) ON DELETE RESTRICT,
    CONSTRAINT boq_mappings_workflow_step_boq_item_key
        UNIQUE (workflow_step_id, boq_item_id),
    CONSTRAINT boq_mappings_allocated_quantity_positive_check CHECK (
        allocated_quantity > 0
    ),
    CONSTRAINT boq_mappings_allocated_cost_non_negative_check CHECK (
        allocated_cost >= 0
    ),
    CONSTRAINT boq_mappings_allocation_percentage_range_check CHECK (
        allocation_percentage IS NULL
        OR (allocation_percentage >= 0 AND allocation_percentage <= 100)
    )
);

COMMENT ON TABLE boq_mappings IS
    'Financial Integration: links WorkflowStep to BOQItem; allocated_weight not used in Phase 1.';
COMMENT ON COLUMN boq_mappings.allocated_quantity IS 'Quantity allocated to WorkflowStep.';
COMMENT ON COLUMN boq_mappings.allocated_cost IS
    'Financial value allocated; app may validate against BOQItem.rate.';

CREATE INDEX idx_boq_mappings_workflow_step_id ON boq_mappings (workflow_step_id);
CREATE INDEX idx_boq_mappings_boq_item_id ON boq_mappings (boq_item_id);

COMMIT;
