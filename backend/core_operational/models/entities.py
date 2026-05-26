from datetime import datetime

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from backend.models.main_models import Base


class Project(Base):
    __tablename__ = "core_operational_projects"

    id = Column(Integer, primary_key=True)
    code = Column(String(60), index=True)
    title = Column(String(160), nullable=False)
    project_type = Column(String(40), nullable=False, default="building")
    description = Column(Text)
    baseline_mode = Column(String(40), default="manual")
    baseline_configuration = Column(JSON, default=dict)
    operational_settings = Column(JSON, default=dict)
    start_at = Column(DateTime)
    target_finish_at = Column(DateTime)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    wbs_templates = relationship(
        "WbsTemplate",
        back_populates="project",
    )
    location_nodes = relationship(
        "LocationNode",
        back_populates="project",
    )
    workflow_nodes = relationship(
        "WorkflowNode",
        back_populates="project",
    )
    workflow_edges = relationship(
        "WorkflowEdge",
        back_populates="project",
    )
    activity_instances = relationship(
        "ActivityInstance",
        back_populates="project",
    )
    resources = relationship(
        "Resource",
        back_populates="project",
    )
    dependencies = relationship(
        "Dependency",
        back_populates="project",
    )


class WbsTemplate(Base):
    __tablename__ = "core_operational_wbs_templates"

    id = Column(Integer, primary_key=True)
    project_id = Column(
        Integer,
        ForeignKey("core_operational_projects.id"),
        nullable=False,
        index=True,
    )
    code = Column(String(80), nullable=False, index=True)
    title = Column(String(160), nullable=False)
    category = Column(String(80), nullable=False)
    phase = Column(String(80), nullable=False)
    description = Column(Text)
    repeatable = Column(Boolean, default=True)
    default_duration_days = Column(Float)
    default_resource_hints = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    project = relationship(
        "Project",
        back_populates="wbs_templates",
    )
    activity_instances = relationship(
        "ActivityInstance",
        back_populates="wbs_template",
    )


class LocationNode(Base):
    __tablename__ = "core_operational_location_nodes"

    id = Column(Integer, primary_key=True)
    project_id = Column(
        Integer,
        ForeignKey("core_operational_projects.id"),
        nullable=False,
        index=True,
    )
    parent_id = Column(
        Integer,
        ForeignKey("core_operational_location_nodes.id"),
        index=True,
    )
    node_type = Column(String(40), nullable=False)
    code = Column(String(80), index=True)
    title = Column(String(160), nullable=False)
    path = Column(String(320))
    level_index = Column(Integer, default=0)
    sort_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    project = relationship(
        "Project",
        back_populates="location_nodes",
    )
    parent = relationship(
        "LocationNode",
        remote_side=[id],
        back_populates="children",
    )
    children = relationship(
        "LocationNode",
        back_populates="parent",
    )
    activity_instances = relationship(
        "ActivityInstance",
        back_populates="location_node",
    )


class WorkflowNode(Base):
    __tablename__ = "core_operational_workflow_nodes"

    id = Column(Integer, primary_key=True)
    project_id = Column(
        Integer,
        ForeignKey("core_operational_projects.id"),
        nullable=False,
        index=True,
    )
    code = Column(String(80), nullable=False, index=True)
    title = Column(String(160), nullable=False)
    node_type = Column(String(40), nullable=False, default="execution")
    category = Column(String(80))
    description = Column(Text)
    is_entry_node = Column(Boolean, default=False)
    is_terminal_node = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    project = relationship(
        "Project",
        back_populates="workflow_nodes",
    )
    outgoing_edges = relationship(
        "WorkflowEdge",
        foreign_keys="WorkflowEdge.from_node_id",
        back_populates="from_node",
    )
    incoming_edges = relationship(
        "WorkflowEdge",
        foreign_keys="WorkflowEdge.to_node_id",
        back_populates="to_node",
    )
    activity_instances = relationship(
        "ActivityInstance",
        back_populates="workflow_node",
    )


class WorkflowEdge(Base):
    __tablename__ = "core_operational_workflow_edges"

    id = Column(Integer, primary_key=True)
    project_id = Column(
        Integer,
        ForeignKey("core_operational_projects.id"),
        nullable=False,
        index=True,
    )
    from_node_id = Column(
        Integer,
        ForeignKey("core_operational_workflow_nodes.id"),
        nullable=False,
        index=True,
    )
    to_node_id = Column(
        Integer,
        ForeignKey("core_operational_workflow_nodes.id"),
        nullable=False,
        index=True,
    )
    edge_type = Column(String(40), nullable=False, default="standard")
    is_optional = Column(Boolean, default=False)
    condition_expression = Column(Text)
    transition_notes = Column(Text)
    priority_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    project = relationship(
        "Project",
        back_populates="workflow_edges",
    )
    from_node = relationship(
        "WorkflowNode",
        foreign_keys=[from_node_id],
        back_populates="outgoing_edges",
    )
    to_node = relationship(
        "WorkflowNode",
        foreign_keys=[to_node_id],
        back_populates="incoming_edges",
    )


class ActivityInstance(Base):
    __tablename__ = "core_operational_activity_instances"

    id = Column(Integer, primary_key=True)
    project_id = Column(
        Integer,
        ForeignKey("core_operational_projects.id"),
        nullable=False,
        index=True,
    )
    wbs_template_id = Column(
        Integer,
        ForeignKey("core_operational_wbs_templates.id"),
        nullable=False,
        index=True,
    )
    location_node_id = Column(
        Integer,
        ForeignKey("core_operational_location_nodes.id"),
        nullable=False,
        index=True,
    )
    workflow_node_id = Column(
        Integer,
        ForeignKey("core_operational_workflow_nodes.id"),
        index=True,
    )
    code = Column(String(120), index=True)
    title = Column(String(200), nullable=False)
    planned_start_at = Column(DateTime)
    planned_finish_at = Column(DateTime)
    baseline_start_at = Column(DateTime)
    baseline_finish_at = Column(DateTime)
    actual_start_at = Column(DateTime)
    actual_finish_at = Column(DateTime)
    progress_percent = Column(Float, default=0)
    operational_status = Column(String(40), default="planned")
    baseline_locked = Column(Boolean, default=False)
    operational_notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    project = relationship(
        "Project",
        back_populates="activity_instances",
    )
    wbs_template = relationship(
        "WbsTemplate",
        back_populates="activity_instances",
    )
    location_node = relationship(
        "LocationNode",
        back_populates="activity_instances",
    )
    workflow_node = relationship(
        "WorkflowNode",
        back_populates="activity_instances",
    )
    predecessor_links = relationship(
        "Dependency",
        foreign_keys="Dependency.successor_activity_id",
        back_populates="successor_activity",
    )
    successor_links = relationship(
        "Dependency",
        foreign_keys="Dependency.predecessor_activity_id",
        back_populates="predecessor_activity",
    )
    assignments = relationship(
        "Assignment",
        back_populates="activity_instance",
    )
    progress_logs = relationship(
        "ProgressLog",
        back_populates="activity_instance",
    )


class Dependency(Base):
    __tablename__ = "core_operational_dependencies"

    id = Column(Integer, primary_key=True)
    project_id = Column(
        Integer,
        ForeignKey("core_operational_projects.id"),
        nullable=False,
        index=True,
    )
    predecessor_activity_id = Column(
        Integer,
        ForeignKey("core_operational_activity_instances.id"),
        nullable=False,
        index=True,
    )
    successor_activity_id = Column(
        Integer,
        ForeignKey("core_operational_activity_instances.id"),
        nullable=False,
        index=True,
    )
    dependency_type = Column(String(10), nullable=False, default="FS")
    lag_value = Column(Float, default=0)
    lag_unit = Column(String(20), default="days")
    is_active = Column(Boolean, default=True)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    project = relationship(
        "Project",
        back_populates="dependencies",
    )
    predecessor_activity = relationship(
        "ActivityInstance",
        foreign_keys=[predecessor_activity_id],
        back_populates="successor_links",
    )
    successor_activity = relationship(
        "ActivityInstance",
        foreign_keys=[successor_activity_id],
        back_populates="predecessor_links",
    )


class Resource(Base):
    __tablename__ = "core_operational_resources"

    id = Column(Integer, primary_key=True)
    project_id = Column(
        Integer,
        ForeignKey("core_operational_projects.id"),
        nullable=False,
        index=True,
    )
    resource_type = Column(String(40), nullable=False)
    code = Column(String(80), index=True)
    title = Column(String(160), nullable=False)
    unit = Column(String(40))
    default_quantity = Column(Float)
    availability_status = Column(String(40), default="available")
    description = Column(Text)
    operational_notes = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    project = relationship(
        "Project",
        back_populates="resources",
    )
    assignments = relationship(
        "Assignment",
        back_populates="resource",
    )


class Assignment(Base):
    __tablename__ = "core_operational_assignments"

    id = Column(Integer, primary_key=True)
    activity_instance_id = Column(
        Integer,
        ForeignKey("core_operational_activity_instances.id"),
        nullable=False,
        index=True,
    )
    resource_id = Column(
        Integer,
        ForeignKey("core_operational_resources.id"),
        nullable=False,
        index=True,
    )
    planned_quantity = Column(Float)
    actual_quantity = Column(Float)
    allocation_start_at = Column(DateTime)
    allocation_finish_at = Column(DateTime)
    assignment_status = Column(String(40), default="planned")
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    activity_instance = relationship(
        "ActivityInstance",
        back_populates="assignments",
    )
    resource = relationship(
        "Resource",
        back_populates="assignments",
    )


class ProgressLog(Base):
    __tablename__ = "core_operational_progress_logs"

    id = Column(Integer, primary_key=True)
    activity_instance_id = Column(
        Integer,
        ForeignKey("core_operational_activity_instances.id"),
        nullable=False,
        index=True,
    )
    reported_by = Column(String(120))
    logged_at = Column(DateTime, default=datetime.utcnow)
    progress_percent = Column(Float, default=0)
    completed_quantity = Column(Float)
    manpower_used = Column(Float)
    material_usage = Column(Float)
    equipment_hours = Column(Float)
    delay_hours = Column(Float)
    operational_notes = Column(Text)
    issues = Column(Text)
    status_snapshot = Column(String(40))

    activity_instance = relationship(
        "ActivityInstance",
        back_populates="progress_logs",
    )
