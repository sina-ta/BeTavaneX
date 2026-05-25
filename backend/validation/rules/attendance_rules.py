from backend.validation.rules.base import (
    ValidationContext,
    ValidationFinding,
)
from backend.validation.utils.enums import (
    ValidationSeverity,
    ValidationTarget,
)
from backend.validation.utils import thresholds


def rule_suspicious_manpower(
    context: ValidationContext,
) -> ValidationFinding | None:
    report = context.report_payload

    if report.manpower_count > thresholds.MAX_MANPOWER_PER_REPORT:
        return ValidationFinding(
            rule_id="suspicious_manpower",
            target=ValidationTarget.ATTENDANCE,
            severity=ValidationSeverity.WARNING,
            passed=False,
            message="Suspicious manpower allocation",
            explanation=(
                f"Manpower count {report.manpower_count} exceeds "
                f"operational threshold {thresholds.MAX_MANPOWER_PER_REPORT}"
            ),
            confidence=0.85,
            affected_entities={
                "manpower_count": report.manpower_count,
            },
            operational_impact="Crew productivity metrics may be unreliable",
        )

    return None


def rule_zero_manpower_with_production(
    context: ValidationContext,
) -> ValidationFinding | None:
    report = context.report_payload

    if report.manpower_count <= 0 and report.actual_qty > 0:
        return ValidationFinding(
            rule_id="zero_manpower_with_production",
            target=ValidationTarget.ATTENDANCE,
            severity=ValidationSeverity.CRITICAL,
            passed=False,
            message="Production reported with zero manpower",
            explanation="Operational inconsistency between output and crew presence",
            confidence=0.92,
            affected_entities={
                "manpower_count": report.manpower_count,
                "actual_qty": report.actual_qty,
            },
            operational_impact="Workforce intelligence scoring may be invalid",
        )

    return None
