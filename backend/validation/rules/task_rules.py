from backend.validation.rules.base import (
    ValidationContext,
    ValidationFinding,
)
from backend.validation.utils.enums import (
    ValidationSeverity,
    ValidationTarget,
)


def rule_invalid_work_order(
    context: ValidationContext,
) -> ValidationFinding | None:
    report = context.report_payload

    if not context.work_order:
        return ValidationFinding(
            rule_id="invalid_work_order",
            target=ValidationTarget.WORK_ORDER,
            severity=ValidationSeverity.CRITICAL,
            passed=False,
            message="Invalid work order reference",
            explanation=(
                f"Work order {report.work_order_id} does not exist"
            ),
            confidence=0.99,
            affected_entities={
                "work_order_id": report.work_order_id,
            },
            operational_impact="Report cannot be linked to operational tasks",
        )

    return ValidationFinding(
        rule_id="invalid_work_order",
        target=ValidationTarget.WORK_ORDER,
        severity=ValidationSeverity.INFO,
        passed=True,
        message="Work order reference valid",
        explanation="Work order exists in operational system",
        confidence=0.99,
    )


def rule_low_progress_without_delay(
    context: ValidationContext,
) -> ValidationFinding | None:
    from backend.validation.utils import thresholds

    report = context.report_payload
    delay = (report.delay_reason or "").strip().lower()

    if (
        report.actual_qty < thresholds.MIN_PROGRESS_WITHOUT_DELAY
        and delay in {"", "none", "n/a"}
    ):
        return ValidationFinding(
            rule_id="low_progress_without_delay",
            target=ValidationTarget.TASK_PROGRESS,
            severity=ValidationSeverity.WARNING,
            passed=False,
            message="Low progress without delay reason",
            explanation=(
                "Minimal output reported but no operational delay documented"
            ),
            confidence=0.82,
            affected_entities={"actual_qty": report.actual_qty},
            operational_impact="Schedule variance explanation missing",
        )

    return None
