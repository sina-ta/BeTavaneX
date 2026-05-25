from backend.lifecycle.utils.enums import (
    EscalationLevel,
    EscalationTrigger,
)


def evaluate_escalation_triggers(
    *,
    open_blocker_count: int = 0,
    validation_critical: bool = False,
    delay_count: int = 0,
    task_state: str | None = None,
) -> list[dict]:
    escalations = []

    if validation_critical:
        escalations.append({
            "trigger_type": EscalationTrigger.VALIDATION_ANOMALY.value,
            "escalation_level": EscalationLevel.LEVEL_2.value,
            "severity": "critical",
            "responsible_role": "Senior Field Validator",
            "operational_impact": (
                "Critical validation anomaly requires review"
            ),
        })

    if open_blocker_count >= 2:
        escalations.append({
            "trigger_type": EscalationTrigger.BLOCKED_TASK.value,
            "escalation_level": EscalationLevel.LEVEL_1.value,
            "severity": "high",
            "responsible_role": "Supervisor",
            "operational_impact": (
                f"{open_blocker_count} operational blockers active"
            ),
        })

    if delay_count >= 3:
        escalations.append({
            "trigger_type": EscalationTrigger.REPEATED_DELAY.value,
            "escalation_level": EscalationLevel.LEVEL_2.value,
            "severity": "warning",
            "responsible_role": "Operations Manager",
            "operational_impact": "Repeated delay pattern detected",
        })

    if task_state == "delayed":
        escalations.append({
            "trigger_type": EscalationTrigger.SCHEDULE_RISK.value,
            "escalation_level": EscalationLevel.LEVEL_1.value,
            "severity": "warning",
            "responsible_role": "Project Manager",
            "operational_impact": "Task execution behind schedule",
        })

    return escalations
