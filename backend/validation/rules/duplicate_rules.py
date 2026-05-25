from backend.validation.rules.base import (
    ValidationContext,
    ValidationFinding,
)
from backend.validation.utils.enums import (
    ValidationSeverity,
    ValidationTarget,
)
from backend.validation.utils import thresholds


def rule_duplicate_report(
    context: ValidationContext,
) -> ValidationFinding | None:
    report = context.report_payload

    for existing in context.work_order_reports:
        qty_match = abs(
            (existing.actual_qty or 0) - report.actual_qty
        ) < thresholds.DUPLICATE_QTY_TOLERANCE

        same_reporter = (
            existing.reported_by == report.reported_by
        )

        if qty_match and same_reporter:
            return ValidationFinding(
                rule_id="duplicate_report",
                target=ValidationTarget.DUPLICATE,
                severity=ValidationSeverity.CRITICAL,
                passed=False,
                message="Duplicate report submission detected",
                explanation=(
                    "Matching quantity and reporter found in prior "
                    "reports for this work order"
                ),
                confidence=0.9,
                affected_entities={
                    "existing_report_id": existing.id,
                    "work_order_id": report.work_order_id,
                },
                operational_impact="KPI double-counting risk",
            )

    return None
