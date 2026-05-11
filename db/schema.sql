CREATE TABLE daily_work_orders (
    id SERIAL PRIMARY KEY,
    project_id INTEGER,
    task_id INTEGER,
    assigned_to VARCHAR(100),
    planned_qty FLOAT,
    unit VARCHAR(20),
    planned_start TIMESTAMP,
    planned_finish TIMESTAMP,
    priority VARCHAR(20),
    status VARCHAR(20),
    created_by VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE daily_reports (
    id SERIAL PRIMARY KEY,
    work_order_id INTEGER REFERENCES daily_work_orders(id),
    reported_by VARCHAR(100),
    actual_qty FLOAT,
    manpower_count INTEGER,
    equipment_hours FLOAT,
    material_consumption FLOAT,
    delay_reason TEXT,
    weather_status VARCHAR(50),
    photo_count INTEGER,
    report_status VARCHAR(20),
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    approved_by VARCHAR(100)
);