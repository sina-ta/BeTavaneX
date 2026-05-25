-- BetavanX Operational Validation & Data Integrity Schema

CREATE TABLE IF NOT EXISTS validation_rules (
    id SERIAL PRIMARY KEY,
    rule_id VARCHAR(80) NOT NULL UNIQUE,
    name VARCHAR(160) NOT NULL,
    target VARCHAR(60) NOT NULL,
    severity_default VARCHAR(20),
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS validation_results (
    id SERIAL PRIMARY KEY,
    entity_type VARCHAR(60) NOT NULL,
    entity_id INTEGER NOT NULL,
    trust_score FLOAT NOT NULL,
    validation_score FLOAT NOT NULL,
    consistency_score FLOAT NOT NULL,
    status VARCHAR(20) NOT NULL,
    summary TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_validation_results_entity
    ON validation_results (entity_type, entity_id);

CREATE TABLE IF NOT EXISTS validation_events (
    id SERIAL PRIMARY KEY,
    validation_result_id INTEGER NOT NULL,
    rule_id VARCHAR(80) NOT NULL,
    target VARCHAR(60) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    passed BOOLEAN NOT NULL,
    message TEXT,
    explanation TEXT,
    confidence FLOAT,
    affected_entities TEXT,
    operational_impact TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS operational_anomalies (
    id SERIAL PRIMARY KEY,
    validation_result_id INTEGER,
    entity_type VARCHAR(60) NOT NULL,
    entity_id INTEGER NOT NULL,
    anomaly_type VARCHAR(80) NOT NULL,
    target VARCHAR(60),
    severity VARCHAR(20) NOT NULL,
    confidence FLOAT,
    explanation TEXT,
    operational_impact TEXT,
    affected_entities TEXT,
    resolved BOOLEAN DEFAULT FALSE,
    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS trust_scores (
    id SERIAL PRIMARY KEY,
    entity_type VARCHAR(60) NOT NULL,
    entity_id INTEGER NOT NULL,
    score_type VARCHAR(60) NOT NULL,
    score FLOAT NOT NULL,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    source VARCHAR(60) DEFAULT 'validation_engine'
);

CREATE TABLE IF NOT EXISTS report_consistency (
    id SERIAL PRIMARY KEY,
    report_id INTEGER NOT NULL UNIQUE,
    consistency_score FLOAT NOT NULL,
    quantity_deviation FLOAT,
    manpower_deviation FLOAT,
    delay_pattern_flag BOOLEAN DEFAULT FALSE,
    metrics TEXT,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS workforce_reliability (
    id SERIAL PRIMARY KEY,
    worker_identifier VARCHAR(120) NOT NULL,
    reporting_reliability FLOAT DEFAULT 50,
    operational_consistency FLOAT DEFAULT 50,
    attendance_trustworthiness FLOAT DEFAULT 50,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_workforce_reliability_identifier
    ON workforce_reliability (worker_identifier);
