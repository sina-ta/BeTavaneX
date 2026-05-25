from backend.validation.rules.base import (
    ValidationContext,
    ValidationFinding,
)
from backend.validation.utils.enums import (
    ValidationSeverity,
    ValidationTarget,
)


def rule_unapproved_submission(
    context: ValidationContext,
) -> ValidationFinding | None:
    report = context.report_payload
    status = (report.report_status or "").strip().lower()

    if status == "draft":
        return ValidationFinding(
            rule_id="unapproved_submission",
            target=ValidationTarget.TIMING,
            severity=ValidationSeverity.INFO,
            passed=True,
            message="Report submitted as draft",
            explanation="Draft reports have reduced operational trust weight",
            confidence=0.95,
        )

    if status not in {"submitted", "approved"}:
        return ValidationFinding(
            rule_id="unapproved_submission",
            target=ValidationTarget.TIMING,
            severity=ValidationSeverity.WARNING,
            passed=False,
            message="Non-standard report status",
            explanation=f"Unexpected status: {report.report_status}",
            confidence=0.7,
            operational_impact="Approval workflow integrity uncertain",
        )

    return None
