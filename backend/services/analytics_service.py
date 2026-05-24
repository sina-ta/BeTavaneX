from datetime import datetime

from backend.database import SessionLocal

from backend.models import KpiHistory

from backend.repositories.kpi_history_repository import (
    KpiHistoryRepository,
)


TREND_THRESHOLD = 0.05


def calculate_trend(
    values: list[float],
) -> str:
    if len(values) < 2:
        return "stable"

    recent = values[-1]
    previous = values[-2]

    if previous == 0:
        return "stable"

    change = (recent - previous) / abs(previous)

    if change > TREND_THRESHOLD:
        return "improving"

    if change < -TREND_THRESHOLD:
        return "declining"

    return "stable"


def record_task_kpis(
    task_id: int,
    kpis: dict,
) -> None:
    session = SessionLocal()

    try:
        repo = KpiHistoryRepository(session)

        repo.create(
            KpiHistory(
                task_id=task_id,
                recorded_at=datetime.utcnow(),
                cpi=kpis["cpi"],
                spi=kpis["spi"],
                progress_percent=kpis["progress_percent"],
                final_score=kpis["final_score"],
                risk_score=kpis["risk_score"],
            )
        )

    finally:
        session.close()


def record_dashboard_kpis(tasks: list[dict]) -> None:
    for task in tasks:
        record_task_kpis(
            task["task_id"],
            task,
        )


def get_task_kpi_trends(
    task_id: int,
    limit: int = 30,
) -> dict:
    session = SessionLocal()

    try:
        repo = KpiHistoryRepository(session)
        records = repo.get_by_task_id(task_id, limit)

        if not records:
            return {
                "task_id": task_id,
                "points": [],
                "trends": {
                    "cpi": "stable",
                    "spi": "stable",
                    "progress": "stable",
                },
            }

        records = list(reversed(records))

        points = [
            {
                "recorded_at": record.recorded_at.isoformat(),
                "cpi": record.cpi,
                "spi": record.spi,
                "progress_percent": record.progress_percent,
                "final_score": record.final_score,
                "risk_score": record.risk_score,
            }
            for record in records
        ]

        return {
            "task_id": task_id,
            "points": points,
            "trends": {
                "cpi": calculate_trend(
                    [point["cpi"] for point in points]
                ),
                "spi": calculate_trend(
                    [point["spi"] for point in points]
                ),
                "progress": calculate_trend(
                    [
                        point["progress_percent"]
                        for point in points
                    ]
                ),
            },
        }

    finally:
        session.close()


def get_project_kpi_trends(limit: int = 30) -> dict:
    session = SessionLocal()

    try:
        repo = KpiHistoryRepository(session)
        snapshots = repo.get_project_averages(limit)

        if not snapshots:
            return {
                "points": [],
                "trends": {
                    "cpi": "stable",
                    "spi": "stable",
                },
            }

        return {
            "points": snapshots,
            "trends": {
                "cpi": calculate_trend(
                    [
                        point["avg_cpi"]
                        for point in snapshots
                    ]
                ),
                "spi": calculate_trend(
                    [
                        point["avg_spi"]
                        for point in snapshots
                    ]
                ),
            },
        }

    finally:
        session.close()
