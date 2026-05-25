from backend.database import SessionLocal

from backend.models import DailyReport

from backend.repositories.report_repository import (
    ReportRepository,
)

from backend.repositories.task_repository import (
    TaskRepository,
)

from backend.validation.repositories.validation_repository import (
    ValidationRepository,
)

from backend.validation.services.pipeline_service import (
    run_daily_report_validation_pipeline,
)


def validate_and_persist_daily_report(
    report_payload,
    work_order,
    report_id: int,
) -> dict:
    session = SessionLocal()

    try:
        report_repo = ReportRepository(session)
        validation_repo = ValidationRepository(session)

        work_order_reports = report_repo.get_by_work_order_id(
            report_payload.work_order_id,
        )
        work_order_reports = [
            r for r in work_order_reports if r.id != report_id
        ]

        pipeline_result = run_daily_report_validation_pipeline(
            report_payload,
            work_order,
            work_order_reports,
            all_reports=report_repo.get_all(),
        )

        validation_repo.persist_report_validation(
            report_id,
            pipeline_result,
        )

        if report_payload.reported_by:
            validation_repo.update_workforce_reliability(
                report_payload.reported_by,
                pipeline_result["workforce_reliability_delta"],
            )

        return pipeline_result

    finally:
        session.close()


def get_trusted_reports(session) -> list[DailyReport]:
    report_repo = ReportRepository(session)
    validation_repo = ValidationRepository(session)

    all_reports = report_repo.get_all()
    trusted_ids = validation_repo.get_trusted_report_ids()

    if not trusted_ids:
        return all_reports

    return [
        report
        for report in all_reports
        if report.id in trusted_ids
    ]


def get_validation_summary_service() -> dict:
    session = SessionLocal()

    try:
        repo = ValidationRepository(session)
        return repo.get_validation_summary()
    finally:
        session.close()


def get_report_validation_service(report_id: int) -> dict:
    session = SessionLocal()

    try:
        repo = ValidationRepository(session)
        result = repo.get_validation_by_report_id(report_id)

        if not result:
            return {"error": "Validation not found"}

        return {
            "report_id": report_id,
            "trust_score": result.trust_score,
            "validation_score": result.validation_score,
            "consistency_score": result.consistency_score,
            "status": result.status,
            "summary": result.summary,
        }
    finally:
        session.close()


def get_active_anomalies_service() -> list[dict]:
    session = SessionLocal()

    try:
        repo = ValidationRepository(session)
        anomalies = repo.get_recent_anomalies()

        return [
            {
                "id": anomaly.id,
                "entity_type": anomaly.entity_type,
                "entity_id": anomaly.entity_id,
                "anomaly_type": anomaly.anomaly_type,
                "severity": anomaly.severity,
                "confidence": anomaly.confidence,
                "explanation": anomaly.explanation,
                "operational_impact": anomaly.operational_impact,
            }
            for anomaly in anomalies
        ]
    finally:
        session.close()


def preview_daily_report_validation(
    report_payload,
    work_order_id: int,
) -> dict:
    session = SessionLocal()

    try:
        task_repo = TaskRepository(session)
        report_repo = ReportRepository(session)

        work_order = task_repo.get_work_order_by_id(work_order_id)
        work_order_reports = report_repo.get_by_work_order_id(
            work_order_id,
        )

        return run_daily_report_validation_pipeline(
            report_payload,
            work_order,
            work_order_reports,
            all_reports=report_repo.get_all(),
        )
    finally:
        session.close()
