import json

from sqlalchemy.orm import Session

from backend.validation.models.entities import (
    ValidationResult,
    ValidationEvent,
    OperationalAnomaly,
    TrustScore,
    ReportConsistency,
    WorkforceReliability,
)
from backend.validation.utils.enums import ValidationStatus


class ValidationRepository:
    def __init__(self, session: Session):
        self.session = session

    def persist_report_validation(
        self,
        report_id: int,
        pipeline_result: dict,
    ) -> ValidationResult:
        result = ValidationResult(
            entity_type="daily_report",
            entity_id=report_id,
            trust_score=pipeline_result["trust_score"],
            validation_score=pipeline_result["validation_score"],
            consistency_score=pipeline_result["consistency_score"],
            status=pipeline_result["status"],
            summary=pipeline_result.get("summary"),
        )

        self.session.add(result)
        self.session.flush()

        for finding in pipeline_result["findings"]:
            self.session.add(
                ValidationEvent(
                    validation_result_id=result.id,
                    rule_id=finding["rule_id"],
                    target=finding["target"],
                    severity=finding["severity"],
                    passed=finding["passed"],
                    message=finding["message"],
                    explanation=finding["explanation"],
                    confidence=finding["confidence"],
                    affected_entities=json.dumps(
                        finding.get("affected_entities", {})
                    ),
                    operational_impact=finding.get(
                        "operational_impact",
                        "",
                    ),
                )
            )

        for anomaly in pipeline_result["anomalies"]:
            self.session.add(
                OperationalAnomaly(
                    validation_result_id=result.id,
                    entity_type="daily_report",
                    entity_id=report_id,
                    anomaly_type=anomaly["anomaly_type"],
                    target=anomaly.get("target"),
                    severity=anomaly["severity"],
                    confidence=anomaly.get("confidence"),
                    explanation=anomaly.get("explanation"),
                    operational_impact=anomaly.get(
                        "operational_impact",
                    ),
                    affected_entities=json.dumps(
                        anomaly.get("affected_entities", {})
                    ),
                )
            )

        self.session.add(
            ReportConsistency(
                report_id=report_id,
                consistency_score=pipeline_result[
                    "consistency_score"
                ],
                delay_pattern_flag=any(
                    a["anomaly_type"] == "repeated_delay_pattern"
                    for a in pipeline_result["anomalies"]
                ),
                metrics=json.dumps({
                    "trust_score": pipeline_result["trust_score"],
                    "validation_score": pipeline_result[
                        "validation_score"
                    ],
                }),
            )
        )

        self.session.add(
            TrustScore(
                entity_type="daily_report",
                entity_id=report_id,
                score_type="operational_trust",
                score=pipeline_result["trust_score"],
            )
        )

        self.session.commit()
        self.session.refresh(result)
        return result

    def update_workforce_reliability(
        self,
        reporter: str,
        delta: float,
    ) -> None:
        record = (
            self.session.query(WorkforceReliability)
            .filter(
                WorkforceReliability.worker_identifier
                == reporter
            )
            .first()
        )

        if not record:
            record = WorkforceReliability(
                worker_identifier=reporter,
                reporting_reliability=50,
                operational_consistency=50,
                attendance_trustworthiness=50,
            )
            self.session.add(record)

        record.reporting_reliability = round(
            min(
                max(record.reporting_reliability + delta, 0),
                100,
            ),
            2,
        )
        record.operational_consistency = round(
            min(
                max(
                    record.operational_consistency
                    + (delta * 0.5),
                    0,
                ),
                100,
            ),
            2,
        )

        self.session.commit()

    def get_trusted_report_ids(self) -> set[int]:
        rows = (
            self.session.query(ValidationResult.entity_id)
            .filter(ValidationResult.entity_type == "daily_report")
            .filter(
                ValidationResult.status.in_([
                    ValidationStatus.TRUSTED.value,
                    ValidationStatus.WARNING.value,
                ])
            )
            .all()
        )

        return {row.entity_id for row in rows}

    def get_validation_by_report_id(
        self,
        report_id: int,
    ) -> ValidationResult | None:
        return (
            self.session.query(ValidationResult)
            .filter(ValidationResult.entity_type == "daily_report")
            .filter(ValidationResult.entity_id == report_id)
            .order_by(ValidationResult.created_at.desc())
            .first()
        )

    def get_recent_anomalies(
        self,
        limit: int = 50,
    ) -> list[OperationalAnomaly]:
        return (
            self.session.query(OperationalAnomaly)
            .filter(OperationalAnomaly.resolved.is_(False))
            .order_by(OperationalAnomaly.detected_at.desc())
            .limit(limit)
            .all()
        )

    def get_validation_summary(self) -> dict:
        total = (
            self.session.query(ValidationResult)
            .filter(ValidationResult.entity_type == "daily_report")
            .count()
        )

        trusted = (
            self.session.query(ValidationResult)
            .filter(ValidationResult.entity_type == "daily_report")
            .filter(
                ValidationResult.status
                == ValidationStatus.TRUSTED.value
            )
            .count()
        )

        anomalies = (
            self.session.query(OperationalAnomaly)
            .filter(OperationalAnomaly.resolved.is_(False))
            .count()
        )

        return {
            "total_validated": total,
            "trusted_count": trusted,
            "active_anomalies": anomalies,
        }
