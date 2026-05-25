from backend.validation.rules.base import (
    ValidationContext,
    ValidationFinding,
)
from backend.validation.utils.enums import (
    ValidationSeverity,
    ValidationTarget,
)
from backend.validation.utils import thresholds


def rule_excessive_equipment_hours(
    context: ValidationContext,
) -> ValidationFinding | None:
    report = context.report_payload

    if report.equipment_hours > thresholds.MAX_EQUIPMENT_HOURS_PER_SHIFT:
        return ValidationFinding(
            rule_id="excessive_equipment_hours",
            target=ValidationTarget.EQUIPMENT,
            severity=ValidationSeverity.WARNING,
            passed=False,
            message="Excessive equipment hours reported",
            explanation=(
                f"Equipment hours {report.equipment_hours} exceed "
                f"shift maximum {thresholds.MAX_EQUIPMENT_HOURS_PER_SHIFT}"
            ),
            confidence=0.87,
            affected_entities={
                "equipment_hours": report.equipment_hours,
            },
            operational_impact="Cost analytics may be inflated",
        )

    return None
