from enum import Enum


class ValidationSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class ValidationTarget(str, Enum):
    DAILY_REPORT = "daily_report"
    ATTENDANCE = "attendance"
    QUANTITY = "quantity"
    TASK_PROGRESS = "task_progress"
    CREW_PRODUCTIVITY = "crew_productivity"
    DELAY = "delay"
    WORK_ORDER = "work_order"
    EQUIPMENT = "equipment"
    TIMING = "timing"
    DUPLICATE = "duplicate"


class ValidationStatus(str, Enum):
    TRUSTED = "trusted"
    WARNING = "warning"
    REJECTED = "rejected"
    PENDING = "pending"


class TrustEntityType(str, Enum):
    DAILY_REPORT = "daily_report"
    WORKER = "worker"
    CREW = "crew"
    WORK_ORDER = "work_order"
