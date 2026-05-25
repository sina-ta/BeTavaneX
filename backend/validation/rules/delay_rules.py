from backend.validation.rules.base import (
    ValidationContext,
    ValidationFinding,
)
from backend.validation.utils.enums import (
    ValidationSeverity,
    ValidationTarget,
)

SUSPICIOUS_DELAY_KEYWORDS = {"", "none", "n/a", "test", "unknown"}


def rule_missing_delay_explanation(
    context: ValidationContext,
) -> ValidationFinding | None:
    report = context.report_payload
    work_order = context.work_order

    if not work_order:
        return None

    if report.actual_qty >= work_order.planned_qty * 0.5:
        return None

    delay = (report.delay_reason or "").strip().lower()

    if delay in SUSPICIOUS_DELAY_KEYWORDS and report.actual_qty < (
        work_order.planned_qty * 0.3
    ):
        return ValidationFinding(
            rule_id="missing_delay_explanation",
            target=ValidationTarget.DELAY,
            severity=ValidationSeverity.WARNING,
            passed=False,
            message="Behind schedule without valid delay reason",
            explanation="Progress lag not explained by field operations",
            confidence=0.8,
            operational_impact="Delay analytics incomplete",
        )

    return None


def rule_repeated_delay_pattern(
    context: ValidationContext,
) -> ValidationFinding | None:
    report = context.report_payload
    delay = (report.delay_reason or "").strip()

    if not delay or delay.lower() in SUSPICIOUS_DELAY_KEYWORDS:
        return None

    prior = context.work_order_reports
    same_delay_count = len([
        r
        for r in prior
        if (r.delay_reason or "").strip() == delay
    ])

    if same_delay_count >= 3:
        return ValidationFinding(
            rule_id="repeated_delay_pattern",
            target=ValidationTarget.DELAY,
            severity=ValidationSeverity.WARNING,
            passed=False,
            message="Repeated suspicious delay reason",
            explanation=(
                f"Delay reason '{delay}' reported {same_delay_count} "
                "times for this work order"
            ),
            confidence=0.75,
            affected_entities={"delay_reason": delay},
            operational_impact="Operational blocker may be misreported",
        )

    return None
