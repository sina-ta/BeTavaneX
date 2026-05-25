-- BetavanX Workforce Intelligence Schema
-- Removes legacy HR tables and creates operational workforce domain.

-- =========================
-- DROP LEGACY HR TABLES
-- =========================

DROP TABLE IF EXISTS worker_equipment CASCADE;
DROP TABLE IF EXISTS worker_certificates CASCADE;
DROP TABLE IF EXISTS worker_training CASCADE;
DROP TABLE IF EXISTS task_assignments CASCADE;
DROP TABLE IF EXISTS worker_scores CASCADE;
DROP TABLE IF EXISTS worker_payments CASCADE;
DROP TABLE IF EXISTS worker_attendance CASCADE;
DROP TABLE IF EXISTS worker_skills CASCADE;
DROP TABLE IF EXISTS workers CASCADE;
DROP TABLE IF EXISTS skills CASCADE;
DROP TABLE IF EXISTS crews CASCADE;
DROP TABLE IF EXISTS roles CASCADE;

-- =========================
-- OPERATIONAL WORKFORCE DOMAIN
-- =========================

CREATE TABLE IF NOT EXISTS workforce_trades (
    id SERIAL PRIMARY KEY,
    name VARCHAR(120) NOT NULL UNIQUE,
    description TEXT
);

CREATE TABLE IF NOT EXISTS workforce_operational_roles (
    id SERIAL PRIMARY KEY,
    name VARCHAR(80) NOT NULL UNIQUE,
    authority_level INTEGER DEFAULT 1,
    description TEXT
);

CREATE TABLE IF NOT EXISTS workforce_medical_statuses (
    id SERIAL PRIMARY KEY,
    name VARCHAR(80) NOT NULL UNIQUE,
    clearance_level VARCHAR(40),
    description VARCHAR
);

CREATE TABLE IF NOT EXISTS workforce_crews (
    id SERIAL PRIMARY KEY,
    name VARCHAR(120) NOT NULL,
    trade VARCHAR(80),
    supervisor VARCHAR(120),
    active_project_id INTEGER,
    performance_score FLOAT,
    utilization_rate FLOAT
);

CREATE TABLE IF NOT EXISTS workforce_workers (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(80) NOT NULL,
    last_name VARCHAR(80) NOT NULL,
    national_id VARCHAR(40) UNIQUE,
    phone VARCHAR(40),
    emergency_contact VARCHAR(120),
    profile_photo VARCHAR,
    trade_id INTEGER REFERENCES workforce_trades(id),
    current_role VARCHAR(80),
    skill_level VARCHAR(40),
    availability_status VARCHAR(40) DEFAULT 'available',
    current_project_id INTEGER,
    current_crew_id INTEGER REFERENCES workforce_crews(id),
    employment_type VARCHAR(40),
    hire_date DATE,
    contract_type VARCHAR(40),
    daily_cost FLOAT,
    payroll_group VARCHAR(80),
    medical_status_id INTEGER REFERENCES workforce_medical_statuses(id),
    insurance_status VARCHAR(40),
    safety_clearance VARCHAR(40),
    accommodation_required BOOLEAN DEFAULT FALSE,
    transportation_required BOOLEAN DEFAULT FALSE,
    home_city VARCHAR(80),
    current_location VARCHAR(120),
    productivity_score FLOAT,
    reliability_score FLOAT,
    safety_score FLOAT,
    teamwork_score FLOAT,
    quality_score FLOAT,
    leadership_score FLOAT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS workforce_skills (
    id SERIAL PRIMARY KEY,
    name VARCHAR(120) NOT NULL UNIQUE,
    category VARCHAR(80),
    description VARCHAR
);

CREATE TABLE IF NOT EXISTS workforce_worker_skills (
    id SERIAL PRIMARY KEY,
    worker_id INTEGER NOT NULL REFERENCES workforce_workers(id),
    skill_id INTEGER NOT NULL REFERENCES workforce_skills(id),
    proficiency_level VARCHAR(40),
    experience_years FLOAT
);

CREATE TABLE IF NOT EXISTS workforce_certifications (
    id SERIAL PRIMARY KEY,
    name VARCHAR(160) NOT NULL UNIQUE,
    issuing_authority VARCHAR(160),
    description VARCHAR
);

CREATE TABLE IF NOT EXISTS workforce_worker_certifications (
    id SERIAL PRIMARY KEY,
    worker_id INTEGER NOT NULL REFERENCES workforce_workers(id),
    certification_id INTEGER NOT NULL REFERENCES workforce_certifications(id),
    issue_date DATE,
    expiry_date DATE,
    status VARCHAR(40) DEFAULT 'active'
);

CREATE TABLE IF NOT EXISTS workforce_assignments (
    id SERIAL PRIMARY KEY,
    worker_id INTEGER NOT NULL REFERENCES workforce_workers(id),
    work_order_id INTEGER,
    task_id INTEGER,
    crew_id INTEGER REFERENCES workforce_crews(id),
    project_id INTEGER,
    assigned_date DATE,
    assigned_by VARCHAR(120),
    status VARCHAR(40) DEFAULT 'assigned',
    readiness_status VARCHAR(40)
);

CREATE TABLE IF NOT EXISTS workforce_attendance (
    id SERIAL PRIMARY KEY,
    worker_id INTEGER NOT NULL REFERENCES workforce_workers(id),
    date DATE NOT NULL,
    shift VARCHAR(40),
    check_in VARCHAR(20),
    check_out VARCHAR(20),
    status VARCHAR(40),
    overtime_hours FLOAT DEFAULT 0,
    absence_reason VARCHAR
);

CREATE TABLE IF NOT EXISTS workforce_performance_metrics (
    id SERIAL PRIMARY KEY,
    worker_id INTEGER NOT NULL REFERENCES workforce_workers(id),
    work_order_id INTEGER,
    daily_report_id INTEGER,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metric_type VARCHAR(60) NOT NULL,
    metric_value FLOAT,
    source VARCHAR(60) DEFAULT 'daily_report',
    notes VARCHAR
);

CREATE TABLE IF NOT EXISTS workforce_accommodations (
    id SERIAL PRIMARY KEY,
    worker_id INTEGER NOT NULL REFERENCES workforce_workers(id),
    location VARCHAR(160),
    status VARCHAR(40),
    check_in_date DATE,
    check_out_date DATE
);

CREATE TABLE IF NOT EXISTS workforce_transport (
    id SERIAL PRIMARY KEY,
    worker_id INTEGER NOT NULL REFERENCES workforce_workers(id),
    transport_type VARCHAR(80),
    route VARCHAR(160),
    status VARCHAR(40),
    assigned_date DATE
);

CREATE TABLE IF NOT EXISTS workforce_contracts (
    id SERIAL PRIMARY KEY,
    worker_id INTEGER NOT NULL REFERENCES workforce_workers(id),
    contract_type VARCHAR(40),
    start_date DATE,
    end_date DATE,
    daily_rate FLOAT,
    status VARCHAR(40)
);

CREATE TABLE IF NOT EXISTS workforce_evaluations (
    id SERIAL PRIMARY KEY,
    worker_id INTEGER NOT NULL REFERENCES workforce_workers(id),
    evaluator VARCHAR(120),
    evaluation_source VARCHAR(60),
    evaluation_date DATE,
    productivity FLOAT,
    reliability FLOAT,
    quality FLOAT,
    safety FLOAT,
    teamwork FLOAT,
    discipline FLOAT,
    leadership FLOAT,
    operational_notes TEXT
);

CREATE TABLE IF NOT EXISTS workforce_availability (
    id SERIAL PRIMARY KEY,
    worker_id INTEGER NOT NULL REFERENCES workforce_workers(id),
    status VARCHAR(40) NOT NULL,
    effective_from TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    effective_until TIMESTAMP,
    reason VARCHAR
);

CREATE TABLE IF NOT EXISTS workforce_fatigue (
    id SERIAL PRIMARY KEY,
    worker_id INTEGER NOT NULL REFERENCES workforce_workers(id),
    fatigue_level FLOAT,
    readiness_score FLOAT,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    source VARCHAR(60) DEFAULT 'manual',
    notes VARCHAR
);

CREATE TABLE IF NOT EXISTS workforce_events (
    id SERIAL PRIMARY KEY,
    worker_id INTEGER REFERENCES workforce_workers(id),
    crew_id INTEGER REFERENCES workforce_crews(id),
    event_type VARCHAR(80) NOT NULL,
    severity VARCHAR(40),
    source VARCHAR(60),
    occurred_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    payload TEXT
);
