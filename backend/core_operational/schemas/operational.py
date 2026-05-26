from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ProjectSchema(BaseModel):
    id: Optional[int] = None
    code: Optional[str] = None
    title: str
    project_type: str = "building"
    description: Optional[str] = None
    baseline_mode: str = "manual"
    baseline_configuration: dict = Field(default_factory=dict)
    operational_settings: dict = Field(default_factory=dict)
    start_at: Optional[datetime] = None
    target_finish_at: Optional[datetime] = None
    is_active: bool = True


class WbsTemplateSchema(BaseModel):
    id: Optional[int] = None
    project_id: int
    code: str
    title: str
    category: str
    phase: str
    description: Optional[str] = None
    repeatable: bool = True
    default_duration_days: Optional[float] = None
    default_resource_hints: dict = Field(default_factory=dict)


class LocationNodeSchema(BaseModel):
    id: Optional[int] = None
    project_id: int
    parent_id: Optional[int] = None
    node_type: str
    code: Optional[str] = None
    title: str
    path: Optional[str] = None
    level_index: int = 0
    sort_order: int = 0
    is_active: bool = True


class WorkflowNodeSchema(BaseModel):
    id: Optional[int] = None
    project_id: int
    code: str
    title: str
    node_type: str = "execution"
    category: Optional[str] = None
    description: Optional[str] = None
    is_entry_node: bool = False
    is_terminal_node: bool = False
    is_active: bool = True


class WorkflowEdgeSchema(BaseModel):
    id: Optional[int] = None
    project_id: int
    from_node_id: int
    to_node_id: int
    edge_type: str = "standard"
    is_optional: bool = False
    condition_expression: Optional[str] = None
    transition_notes: Optional[str] = None
    priority_order: int = 0


class ActivityInstantiationSchema(BaseModel):
    project_id: int
    wbs_template_id: int
    location_node_id: int
    workflow_node_id: Optional[int] = None
    title_override: Optional[str] = None
    planned_start_at: Optional[datetime] = None
    planned_finish_at: Optional[datetime] = None
    baseline_start_at: Optional[datetime] = None
    baseline_finish_at: Optional[datetime] = None
    operational_notes: Optional[str] = None


class ActivityInstanceSchema(BaseModel):
    id: Optional[int] = None
    project_id: int
    wbs_template_id: int
    location_node_id: int
    workflow_node_id: Optional[int] = None
    code: Optional[str] = None
    title: str
    planned_start_at: Optional[datetime] = None
    planned_finish_at: Optional[datetime] = None
    baseline_start_at: Optional[datetime] = None
    baseline_finish_at: Optional[datetime] = None
    actual_start_at: Optional[datetime] = None
    actual_finish_at: Optional[datetime] = None
    progress_percent: float = 0.0
    operational_status: str = "planned"
    baseline_locked: bool = False
    operational_notes: Optional[str] = None


class DependencySchema(BaseModel):
    id: Optional[int] = None
    project_id: int
    predecessor_activity_id: int
    successor_activity_id: int
    dependency_type: str = "FS"
    lag_value: float = 0.0
    lag_unit: str = "days"
    is_active: bool = True
    notes: Optional[str] = None


class ResourceSchema(BaseModel):
    id: Optional[int] = None
    project_id: int
    resource_type: str
    code: Optional[str] = None
    title: str
    unit: Optional[str] = None
    default_quantity: Optional[float] = None
    availability_status: str = "available"
    description: Optional[str] = None
    operational_notes: Optional[str] = None
    is_active: bool = True


class AssignmentSchema(BaseModel):
    id: Optional[int] = None
    activity_instance_id: int
    resource_id: int
    planned_quantity: Optional[float] = None
    actual_quantity: Optional[float] = None
    allocation_start_at: Optional[datetime] = None
    allocation_finish_at: Optional[datetime] = None
    assignment_status: str = "planned"
    notes: Optional[str] = None


class ProgressLogSchema(BaseModel):
    id: Optional[int] = None
    activity_instance_id: int
    reported_by: Optional[str] = None
    logged_at: Optional[datetime] = None
    progress_percent: float = 0.0
    completed_quantity: Optional[float] = None
    manpower_used: Optional[float] = None
    material_usage: Optional[float] = None
    equipment_hours: Optional[float] = None
    delay_hours: Optional[float] = None
    operational_notes: Optional[str] = None
    issues: Optional[str] = None
    status_snapshot: Optional[str] = None
