-- BetavanX Operational Lifecycle & Execution State Schema

CREATE TABLE IF NOT EXISTS lifecycle_task_states (
    id SERIAL PRIMARY KEY,
    task_id INTEGER NOT NULL UNIQUE,
    work_order_id INTEGER,
    current_state VARCHAR(40) NOT NULL DEFAULT 'planned',
    maturity_level VARCHAR(40) DEFAULT 'initial',
    responsible_entity VARCHAR(120),
    operational_notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_lifecycle_task_states_task
    ON lifecycle_task_states (task_id);

CREATE TABLE IF NOT EXISTS lifecycle_work_order_states (
    id SERIAL PRIMARY KEY,
    work_order_id INTEGER NOT NULL UNIQUE,
    task_id INTEGER,
    current_state VARCHAR(40) NOT NULL DEFAULT 'created',
    responsible_entity VARCHAR(120),
    approved_by VARCHAR(120),
    approved_at TIMESTAMP,
    activated_at TIMESTAMP,
    completed_at TIMESTAMP,
    closed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS lifecycle_transitions (
    id SERIAL PRIMARY KEY,
    entity_type VARCHAR(40) NOT NULL,
    entity_id INTEGER NOT NULL,
    from_state VARCHAR(40),
    to_state VARCHAR(40) NOT NULL,
    triggered_by VARCHAR(120),
    reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS lifecycle_blockers (
    id SERIAL PRIMARY KEY,
    entity_type VARCHAR(40) NOT NULL,
    entity_id INTEGER NOT NULL,
    task_id INTEGER,
    work_order_id INTEGER,
    blocker_type VARCHAR(40) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    operational_impact TEXT,
    expected_delay_days FLOAT,
    responsible_entity VARCHAR(120),
    resolution_state VARCHAR(40) DEFAULT 'open',
    resolved_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS lifecycle_dependencies (
    id SERIAL PRIMARY KEY,
    dependent_entity_type VARCHAR(40) NOT NULL,
    dependent_entity_id INTEGER NOT NULL,
    dependency_type VARCHAR(40) NOT NULL,
    depends_on_entity_type VARCHAR(40),
    depends_on_entity_id INTEGER,
    is_satisfied BOOLEAN DEFAULT FALSE,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS lifecycle_approvals (
    id SERIAL PRIMARY KEY,
    entity_type VARCHAR(40) NOT NULL,
    entity_id INTEGER NOT NULL,
    approval_chain_level INTEGER DEFAULT 1,
    required_role VARCHAR(80) NOT NULL,
    status VARCHAR(40) DEFAULT 'pending',
    requested_by VARCHAR(120),
    decided_by VARCHAR(120),
    decision_notes TEXT,
    requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    decided_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS lifecycle_escalations (
    id SERIAL PRIMARY KEY,
    entity_type VARCHAR(40) NOT NULL,
    entity_id INTEGER NOT NULL,
    task_id INTEGER,
    work_order_id INTEGER,
    trigger_type VARCHAR(60) NOT NULL,
    escalation_level VARCHAR(20) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    responsible_role VARCHAR(80),
    operational_impact TEXT,
    resolution_state VARCHAR(40) DEFAULT 'open',
    resolved_by VARCHAR(120),
    resolved_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS lifecycle_readiness (
    id SERIAL PRIMARY KEY,
    entity_type VARCHAR(40) NOT NULL,
    entity_id INTEGER NOT NULL,
    task_id INTEGER,
    readiness_status VARCHAR(40) NOT NULL,
    readiness_score FLOAT,
    factors TEXT,
    evaluated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS lifecycle_timeline_events (
    id SERIAL PRIMARY KEY,
    entity_type VARCHAR(40) NOT NULL,
    entity_id INTEGER NOT NULL,
    task_id INTEGER,
    work_order_id INTEGER,
    event_type VARCHAR(40) NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    severity VARCHAR(20),
    payload TEXT,
    recorded_by VARCHAR(120),
    occurred_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_lifecycle_timeline_entity
    ON lifecycle_timeline_events (entity_type, entity_id);
