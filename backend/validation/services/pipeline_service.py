from backend.validation.rules.base import ValidationContext
from backend.validation.evaluators.report_evaluator import (
    evaluate_daily_report,
)
from backend.validation.anomalies.heuristics import (
    findings_to_anomalies,
)
from backend.validation.scoring.trust_scoring import (
    compute_validation_score,
    compute_trust_score,
    compute_consistency_score,
    resolve_validation_status,
    compute_workforce_reliability_delta,
)


def _serialize_finding(finding) -> dict:
    return {
        "rule_id": finding.rule_id,
        "target": finding.target.value,
        "severity": finding.severity.value,
        "passed": finding.passed,
        "message": finding.message,
        "explanation": finding.explanation,
        "confidence": finding.confidence,
        "affected_entities": finding.affected_entities,
        "operational_impact": finding.operational_impact,
    }


def run_daily_report_validation_pipeline(
    report_payload,
    work_order,
    work_order_reports,
    all_reports=None,
) -> dict:
    """Validate daily report BEFORE analytics consumption."""
    context = ValidationContext(
        report_payload=report_payload,
        work_order=work_order,
        work_order_reports=work_order_reports,
        all_reports=all_reports or [],
    )

    findings = evaluate_daily_report(context)
    anomalies = findings_to_anomalies(findings)

    validation_score = compute_validation_score(findings)
    trust_score = compute_trust_score(findings)
    consistency_score = compute_consistency_score(findings)
    status = resolve_validation_status(
        trust_score,
        findings,
    ).value

    warnings = [
        f"⚠️ {finding.message}"
        for finding in findings
        if not finding.passed
    ]

    failed_count = len([f for f in findings if not f.passed])

    return {
        "trusted": status == "trusted",
        "status": status,
        "trust_score": trust_score,
        "validation_score": validation_score,
        "consistency_score": consistency_score,
        "findings": [_serialize_finding(f) for f in findings],
        "anomalies": anomalies,
        "warnings": warnings,
        "summary": (
            f"{failed_count} validation issue(s) detected"
            if failed_count
            else "Operational data passed validation"
        ),
        "workforce_reliability_delta": (
            compute_workforce_reliability_delta(findings)
        ),
    }
