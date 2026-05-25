from backend.validation.rules.base import ValidationFinding
from backend.validation.utils.enums import ValidationSeverity


def findings_to_anomalies(
    findings: list[ValidationFinding],
) -> list[dict]:
    anomalies = []

    for finding in findings:
        if finding.passed:
            continue

        if finding.severity in {
            ValidationSeverity.WARNING,
            ValidationSeverity.CRITICAL,
        }:
            anomalies.append({
                "anomaly_type": finding.rule_id,
                "target": finding.target.value,
                "severity": finding.severity.value,
                "confidence": finding.confidence,
                "explanation": finding.explanation,
                "message": finding.message,
                "affected_entities": finding.affected_entities,
                "operational_impact": finding.operational_impact,
            })

    return anomalies
