from enum import Enum


class TaskLifecycleState(str, Enum):
    PLANNED = "planned"
    READY = "ready"
    ASSIGNED = "assigned"
    MOBILIZED = "mobilized"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    DELAYED = "delayed"
    UNDER_REVIEW = "under_review"
    COMPLETED = "completed"
    VALIDATED = "validated"
    REJECTED = "rejected"
    ARCHIVED = "archived"


class WorkOrderLifecycleState(str, Enum):
    CREATED = "created"
    APPROVED = "approved"
    ASSIGNED = "assigned"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    COMPLETED = "completed"
    VALIDATED = "validated"
    CLOSED = "closed"


class BlockerType(str, Enum):
    PREDECESSOR_TASK = "predecessor_task"
    CREW = "crew"
    MATERIAL = "material"
    EQUIPMENT = "equipment"
    APPROVAL = "approval"
    SAFETY = "safety"
    ENVIRONMENT = "environment"
    VALIDATION = "validation"


class BlockerSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class BlockerResolutionState(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    ESCALATED = "escalated"


class ApprovalEntityType(str, Enum):
    DAILY_REPORT = "daily_report"
    WORK_ORDER = "work_order"
    TASK_COMPLETION = "task_completion"
    VALIDATION = "validation"
    ESCALATION = "escalation"


class ApprovalStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    ESCALATED = "escalated"


class EscalationLevel(str, Enum):
    LEVEL_1 = "level_1"
    LEVEL_2 = "level_2"
    LEVEL_3 = "level_3"
    EXECUTIVE = "executive"


class EscalationTrigger(str, Enum):
    VALIDATION_ANOMALY = "validation_anomaly"
    REPEATED_DELAY = "repeated_delay"
    UNSAFE_CONDITION = "unsafe_condition"
    WORKFORCE_SHORTAGE = "workforce_shortage"
    BLOCKED_TASK = "blocked_task"
    PRODUCTIVITY_ANOMALY = "productivity_anomaly"
    SCHEDULE_RISK = "schedule_risk"


class ReadinessStatus(str, Enum):
    NOT_READY = "not_ready"
    PARTIALLY_READY = "partially_ready"
    READY = "ready"
    BLOCKED = "blocked"


class TimelineEventType(str, Enum):
    STATE_TRANSITION = "state_transition"
    CREW_ASSIGNMENT = "crew_assignment"
    APPROVAL = "approval"
    ESCALATION = "escalation"
    BLOCKER = "blocker"
    VALIDATION = "validation"
    INCIDENT = "incident"
    READINESS = "readiness"
