from pydantic import BaseModel


class WorkOrderCreate(BaseModel):

    project_id: int
    task_id: int
    assigned_to: str
    planned_qty: float
    unit: str
    priority: str
    status: str
    created_by: str


class DailyReportCreate(BaseModel):

    work_order_id: int
    reported_by: str
    actual_qty: float
    manpower_count: int
    equipment_hours: float
    material_consumption: float
    delay_reason: str
    weather_status: str
    photo_count: int
    report_status: str
    approved_by: str