from sqlalchemy.orm import Session

from backend.models import KpiHistory


class KpiHistoryRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, record: KpiHistory) -> KpiHistory:
        self.session.add(record)
        self.session.commit()
        self.session.refresh(record)
        return record

    def get_by_task_id(
        self,
        task_id: int,
        limit: int = 30,
    ) -> list[KpiHistory]:
        return (
            self.session.query(KpiHistory)
            .filter(KpiHistory.task_id == task_id)
            .order_by(KpiHistory.recorded_at.desc())
            .limit(limit)
            .all()
        )

    def get_recent_for_tasks(
        self,
        task_ids: list[int],
        limit_per_task: int = 10,
    ) -> list[KpiHistory]:
        if not task_ids:
            return []

        return (
            self.session.query(KpiHistory)
            .filter(KpiHistory.task_id.in_(task_ids))
            .order_by(
                KpiHistory.task_id,
                KpiHistory.recorded_at.desc(),
            )
            .all()
        )

    def get_project_averages(
        self,
        limit: int = 30,
    ) -> list[dict]:
        records = (
            self.session.query(KpiHistory)
            .order_by(KpiHistory.recorded_at.desc())
            .limit(limit * 10)
            .all()
        )

        grouped: dict[str, dict] = {}

        for record in records:
            key = record.recorded_at.isoformat()

            if key not in grouped:
                grouped[key] = {
                    "recorded_at": key,
                    "cpi_values": [],
                    "spi_values": [],
                }

            grouped[key]["cpi_values"].append(record.cpi)
            grouped[key]["spi_values"].append(record.spi)

        snapshots = []

        for snapshot in grouped.values():
            cpi_values = snapshot["cpi_values"]
            spi_values = snapshot["spi_values"]

            snapshots.append({
                "recorded_at": snapshot["recorded_at"],
                "avg_cpi": round(
                    sum(cpi_values) / len(cpi_values),
                    2,
                ),
                "avg_spi": round(
                    sum(spi_values) / len(spi_values),
                    2,
                ),
            })

        snapshots.sort(
            key=lambda item: item["recorded_at"],
        )

        return snapshots[-limit:]
