from backend.validation.rules.base import ValidationFinding
from backend.validation.utils.enums import (
    ValidationSeverity,
    ValidationStatus,
)
from backend.validation.utils import thresholds


SEVERITY_PENALTIES = {
    ValidationSeverity.INFO: 3,
    ValidationSeverity.WARNING: 12,
    ValidationSeverity.CRITICAL: 28,
}


def compute_validation_score(
    findings: list[ValidationFinding],
) -> float:
    if not findings:
        return 100.0

    passed = len([f for f in findings if f.passed])
    return round((passed / len(findings)) * 100, 2)


def compute_trust_score(
    findings: list[ValidationFinding],
) -> float:
    score = 100.0

    for finding in findings:
        if finding.passed:
            continue

        score -= SEVERITY_PENALTIES.get(
            finding.severity,
            10,
        )

    return round(max(score, 0), 2)


def compute_consistency_score(
    findings: list[ValidationFinding],
) -> float:
    consistency_rules = {
        "quantity_spike",
        "duplicate_report",
        "zero_manpower_with_production",
        "impossible_productivity",
        "repeated_delay_pattern",
    }

    related = [
        f for f in findings if f.rule_id in consistency_rules
    ]

    if not related:
        return 100.0

    failed = len([f for f in related if not f.passed])
    return round(max(100 - (failed * 20), 0), 2)


def resolve_validation_status(
    trust_score: float,
    findings: list[ValidationFinding],
) -> ValidationStatus:
    critical_failures = [
        f
        for f in findings
        if not f.passed
        and f.severity == ValidationSeverity.CRITICAL
    ]

    if critical_failures:
        return ValidationStatus.REJECTED

    if trust_score >= thresholds.TRUST_THRESHOLD:
        return ValidationStatus.TRUSTED

    return ValidationStatus.WARNING


def compute_workforce_reliability_delta(
    findings: list[ValidationFinding],
) -> float:
    """Operational reliability impact for reporter/workforce."""
    failed = len([f for f in findings if not f.passed])

    if failed == 0:
        return 2.0

    return round(max(-failed * 3, -15), 2)
