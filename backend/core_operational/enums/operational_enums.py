from enum import Enum


class ProjectType(str, Enum):
    BUILDING = "building"
    INFRASTRUCTURE = "infrastructure"
    INDUSTRIAL = "industrial"
    MIXED_USE = "mixed_use"
    INTERIOR_FIT_OUT = "interior_fit_out"


class BaselineMode(str, Enum):
    MANUAL = "manual"
    TEMPLATE_DRIVEN = "template_driven"
    ROLLING = "rolling"


class LocationNodeType(str, Enum):
    PROJECT = "project"
    TOWER = "tower"
    BLOCK = "block"
    BASEMENT = "basement"
    FLOOR = "floor"
    ZONE = "zone"
    ROOM = "room"
    SECTOR = "sector"
    AREA = "area"


class WorkflowNodeType(str, Enum):
    EXECUTION = "execution"
    INSPECTION = "inspection"
    HANDOFF = "handoff"
    MILESTONE = "milestone"


class WorkflowEdgeType(str, Enum):
    STANDARD = "standard"
    OPTIONAL = "optional"
    CONDITIONAL = "conditional"
    PARALLEL = "parallel"


class ActivityStatus(str, Enum):
    PLANNED = "planned"
    READY = "ready"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class DependencyType(str, Enum):
    FS = "FS"
    SS = "SS"
    FF = "FF"


class ResourceType(str, Enum):
    MANPOWER = "manpower"
    MATERIAL = "material"
    EQUIPMENT = "equipment"


class AssignmentStatus(str, Enum):
    PLANNED = "planned"
    ACTIVE = "active"
    RELEASED = "released"
    COMPLETED = "completed"
