from backend.validation.rules.base import (
    ValidationContext,
    ValidationFinding,
)
from backend.validation.rules import DAILY_REPORT_RULES


def evaluate_daily_report(
    context: ValidationContext,
) -> list[ValidationFinding]:
    findings: list[ValidationFinding] = []

    for rule in DAILY_REPORT_RULES:
        result = rule.evaluate(context)

        if result is not None:
            findings.append(result)

    return findings
