from sqlalchemy.orm import Session

from backend.models.hr_models import (
    Worker,
    WorkerAttendance,
    WorkerScore,
    TaskAssignment,
)


class WorkerRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_all(self) -> list[Worker]:
        return self.session.query(Worker).all()

    def get_by_id(self, worker_id: int) -> Worker | None:
        return (
            self.session.query(Worker)
            .filter(Worker.id == worker_id)
            .first()
        )

    def get_attendance_by_worker_id(
        self,
        worker_id: int,
    ) -> list[WorkerAttendance]:
        return (
            self.session.query(WorkerAttendance)
            .filter(WorkerAttendance.worker_id == worker_id)
            .all()
        )

    def get_latest_score_by_worker_id(
        self,
        worker_id: int,
    ) -> WorkerScore | None:
        return (
            self.session.query(WorkerScore)
            .filter(WorkerScore.worker_id == worker_id)
            .order_by(WorkerScore.score_date.desc())
            .first()
        )

    def get_assignments_by_worker_id(
        self,
        worker_id: int,
    ) -> list[TaskAssignment]:
        return (
            self.session.query(TaskAssignment)
            .filter(TaskAssignment.worker_id == worker_id)
            .all()
        )

    def get_crew_worker_ids(
        self,
        crew_id: int,
    ) -> list[int]:
        workers = (
            self.session.query(Worker.id)
            .filter(Worker.crew_id == crew_id)
            .all()
        )

        return [worker.id for worker in workers]
