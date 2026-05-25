from sqlalchemy.orm import Session, joinedload

from backend.workforce.models.worker import Worker
from backend.workforce.models.crew import Crew
from backend.workforce.models.assignment import Assignment
from backend.workforce.models.attendance import Attendance
from backend.workforce.models.evaluation import WorkerEvaluation
from backend.workforce.models.performance import PerformanceMetric
from backend.workforce.models.skill import WorkerSkill, WorkerCertification


class WorkerRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_all_active(self) -> list[Worker]:
        return (
            self.session.query(Worker)
            .options(
                joinedload(Worker.trade),
                joinedload(Worker.crew),
            )
            .filter(Worker.is_active.is_(True))
            .all()
        )

    def get_by_id(self, worker_id: int) -> Worker | None:
        return (
            self.session.query(Worker)
            .options(
                joinedload(Worker.trade),
                joinedload(Worker.crew),
                joinedload(Worker.skills).joinedload(
                    WorkerSkill.skill
                ),
                joinedload(Worker.certifications).joinedload(
                    WorkerCertification.certification
                ),
            )
            .filter(Worker.id == worker_id)
            .first()
        )

    def get_assignments(
        self,
        worker_id: int,
    ) -> list[Assignment]:
        return (
            self.session.query(Assignment)
            .filter(Assignment.worker_id == worker_id)
            .all()
        )

    def get_attendance(
        self,
        worker_id: int,
    ) -> list[Attendance]:
        return (
            self.session.query(Attendance)
            .filter(Attendance.worker_id == worker_id)
            .all()
        )

    def get_evaluations(
        self,
        worker_id: int,
    ) -> list[WorkerEvaluation]:
        return (
            self.session.query(WorkerEvaluation)
            .filter(WorkerEvaluation.worker_id == worker_id)
            .order_by(WorkerEvaluation.evaluation_date.desc())
            .all()
        )

    def get_performance_metrics(
        self,
        worker_id: int,
    ) -> list[PerformanceMetric]:
        return (
            self.session.query(PerformanceMetric)
            .filter(PerformanceMetric.worker_id == worker_id)
            .all()
        )


class CrewRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_all(self) -> list[Crew]:
        return self.session.query(Crew).all()

    def get_by_id(self, crew_id: int) -> Crew | None:
        return (
            self.session.query(Crew)
            .filter(Crew.id == crew_id)
            .first()
        )

    def count_workers(self, crew_id: int) -> int:
        return (
            self.session.query(Worker)
            .filter(Worker.current_crew_id == crew_id)
            .count()
        )
