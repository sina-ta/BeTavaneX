from backend.validation.rules.base import (
    ValidationContext,
    ValidationFinding,
)
from backend.validation.utils.enums import (
    ValidationSeverity,
    ValidationTarget,
)


def rule_impossible_productivity(
    context: ValidationContext,
) -> ValidationFinding | None:
    report = context.report_payload

    if report.manpower_count <= 0:
        return None

    qty_per_worker = report.actual_qty / report.manpower_count

    # Heuristic: >500 units per worker per day is suspicious
    if qty_per_worker > 500:
        return ValidationFinding(
            rule_id="impossible_productivity",
            target=ValidationTarget.CREW_PRODUCTIVITY,
            severity=ValidationSeverity.WARNING,
            passed=False,
            message="Impossible productivity rate detected",
            explanation=(
                f"Output per worker ({qty_per_worker:.1f}) exceeds "
                "realistic field productivity"
            ),
            confidence=0.78,
            affected_entities={
                "qty_per_worker": round(qty_per_worker, 2),
            },
            operational_impact="Productivity analytics may be inflated",
        )

    return None
