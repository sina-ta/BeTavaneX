from enum import Enum


class AvailabilityStatus(str, Enum):
    AVAILABLE = "available"
    ASSIGNED = "assigned"
    ON_LEAVE = "on_leave"
    UNAVAILABLE = "unavailable"


class AssignmentStatus(str, Enum):
    ASSIGNED = "assigned"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class AttendanceStatus(str, Enum):
    PRESENT = "present"
    ABSENT = "absent"
    LATE = "late"
    OVERTIME = "overtime"


class EvaluationSource(str, Enum):
    SUPERVISOR = "supervisor"
    FIELD_VALIDATOR = "field_validator"
    CROSS_REPORT = "cross_report"
    OPERATIONAL_ENGINE = "operational_engine"
    ANALYTICS_ENGINE = "analytics_engine"


class ScoreDimension(str, Enum):
    PRODUCTIVITY = "productivity"
    RELIABILITY = "reliability"
    QUALITY = "quality"
    SAFETY = "safety"
    TEAMWORK = "teamwork"
    DISCIPLINE = "discipline"
    LEADERSHIP = "leadership"
