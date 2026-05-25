from backend.validation.rules.base import (
    RegisteredRule,
    ValidationContext,
    ValidationFinding,
)
from backend.validation.rules.quantity_rules import (
    rule_quantity_exceeds_planned,
    rule_unrealistic_daily_quantity,
    rule_quantity_spike,
)
from backend.validation.rules.attendance_rules import (
    rule_suspicious_manpower,
    rule_zero_manpower_with_production,
)
from backend.validation.rules.productivity_rules import (
    rule_impossible_productivity,
)
from backend.validation.rules.task_rules import (
    rule_invalid_work_order,
    rule_low_progress_without_delay,
)
from backend.validation.rules.delay_rules import (
    rule_missing_delay_explanation,
    rule_repeated_delay_pattern,
)
from backend.validation.rules.duplicate_rules import (
    rule_duplicate_report,
)
from backend.validation.rules.equipment_rules import (
    rule_excessive_equipment_hours,
)
from backend.validation.rules.timing_rules import (
    rule_unapproved_submission,
)
from backend.validation.utils.enums import ValidationTarget


DAILY_REPORT_RULES: list[RegisteredRule] = [
    RegisteredRule(
        "invalid_work_order",
        "Work Order Validity",
        ValidationTarget.WORK_ORDER,
        rule_invalid_work_order,
    ),
    RegisteredRule(
        "duplicate_report",
        "Duplicate Detection",
        ValidationTarget.DUPLICATE,
        rule_duplicate_report,
    ),
    RegisteredRule(
        "quantity_exceeds_planned",
        "Quantity vs Plan",
        ValidationTarget.QUANTITY,
        rule_quantity_exceeds_planned,
    ),
    RegisteredRule(
        "unrealistic_daily_quantity",
        "Quantity Ceiling",
        ValidationTarget.QUANTITY,
        rule_unrealistic_daily_quantity,
    ),
    RegisteredRule(
        "quantity_spike",
        "Quantity Spike",
        ValidationTarget.QUANTITY,
        rule_quantity_spike,
    ),
    RegisteredRule(
        "suspicious_manpower",
        "Manpower Allocation",
        ValidationTarget.ATTENDANCE,
        rule_suspicious_manpower,
    ),
    RegisteredRule(
        "zero_manpower_with_production",
        "Manpower Consistency",
        ValidationTarget.ATTENDANCE,
        rule_zero_manpower_with_production,
    ),
    RegisteredRule(
        "impossible_productivity",
        "Productivity Heuristic",
        ValidationTarget.CREW_PRODUCTIVITY,
        rule_impossible_productivity,
    ),
    RegisteredRule(
        "low_progress_without_delay",
        "Progress vs Delay",
        ValidationTarget.TASK_PROGRESS,
        rule_low_progress_without_delay,
    ),
    RegisteredRule(
        "missing_delay_explanation",
        "Delay Explanation",
        ValidationTarget.DELAY,
        rule_missing_delay_explanation,
    ),
    RegisteredRule(
        "repeated_delay_pattern",
        "Delay Pattern",
        ValidationTarget.DELAY,
        rule_repeated_delay_pattern,
    ),
    RegisteredRule(
        "excessive_equipment_hours",
        "Equipment Usage",
        ValidationTarget.EQUIPMENT,
        rule_excessive_equipment_hours,
    ),
    RegisteredRule(
        "unapproved_submission",
        "Report Status",
        ValidationTarget.TIMING,
        rule_unapproved_submission,
    ),
]
