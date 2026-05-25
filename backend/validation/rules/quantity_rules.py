from backend.validation.rules.base import (
    ValidationContext,
    ValidationFinding,
)
from backend.validation.utils.enums import (
    ValidationSeverity,
    ValidationTarget,
)
from backend.validation.utils import thresholds


def rule_quantity_exceeds_planned(
    context: ValidationContext,
) -> ValidationFinding | None:
    report = context.report_payload
    work_order = context.work_order

    if not work_order:
        return None

    if report.actual_qty > work_order.planned_qty:
        return ValidationFinding(
            rule_id="quantity_exceeds_planned",
            target=ValidationTarget.QUANTITY,
            severity=ValidationSeverity.WARNING,
            passed=False,
            message="Actual quantity exceeds planned quantity",
            explanation=(
                f"Reported {report.actual_qty} exceeds planned "
                f"{work_order.planned_qty} for work order "
                f"{work_order.id}"
            ),
            confidence=0.9,
            affected_entities={
                "work_order_id": work_order.id,
                "actual_qty": report.actual_qty,
                "planned_qty": work_order.planned_qty,
            },
            operational_impact="KPI cost/schedule variance may be distorted",
        )

    return ValidationFinding(
        rule_id="quantity_exceeds_planned",
        target=ValidationTarget.QUANTITY,
        severity=ValidationSeverity.INFO,
        passed=True,
        message="Quantity within planned bounds",
        explanation="Reported quantity does not exceed plan",
        confidence=0.95,
    )


def rule_unrealistic_daily_quantity(
    context: ValidationContext,
) -> ValidationFinding | None:
    report = context.report_payload

    if report.actual_qty > thresholds.MAX_DAILY_QUANTITY:
        return ValidationFinding(
            rule_id="unrealistic_daily_quantity",
            target=ValidationTarget.QUANTITY,
            severity=ValidationSeverity.CRITICAL,
            passed=False,
            message="Unrealistic production quantity reported",
            explanation=(
                f"Quantity {report.actual_qty} exceeds operational "
                f"ceiling {thresholds.MAX_DAILY_QUANTITY}"
            ),
            confidence=0.88,
            affected_entities={"actual_qty": report.actual_qty},
            operational_impact="Analytics and KPIs may be corrupted",
        )

    return None


def rule_quantity_spike(
    context: ValidationContext,
) -> ValidationFinding | None:
    report = context.report_payload
    prior = context.work_order_reports

    if len(prior) < 1:
        return None

    avg_qty = sum(r.actual_qty or 0 for r in prior) / len(prior)

    if avg_qty <= 0:
        return None

    ratio = report.actual_qty / avg_qty

    if ratio > thresholds.MAX_QUANTITY_SPIKE_RATIO:
        return ValidationFinding(
            rule_id="quantity_spike",
            target=ValidationTarget.QUANTITY,
            severity=ValidationSeverity.WARNING,
            passed=False,
            message="Suspicious quantity spike detected",
            explanation=(
                f"Reported quantity is {ratio:.1f}x the historical "
                f"average for this work order"
            ),
            confidence=0.8,
            affected_entities={
                "ratio": round(ratio, 2),
                "historical_avg": round(avg_qty, 2),
            },
            operational_impact="Trend analytics may show false improvement",
        )

    return None
