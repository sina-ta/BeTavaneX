from backend.database import SessionLocal

from backend.repositories.worker_repository import (
    WorkerRepository,
)


def get_workers_service():
    session = SessionLocal()

    try:
        repo = WorkerRepository(session)
        workers = repo.get_all()

        return [
            {
                "id": worker.id,
                "full_name": worker.full_name,
                "role": (
                    worker.role.title
                    if worker.role
                    else "-"
                ),
                "crew": (
                    worker.crew.name
                    if worker.crew
                    else "-"
                ),
                "daily_wage": worker.daily_wage,
                "score": worker.score,
                "status": worker.status,
            }
            for worker in workers
        ]

    finally:
        session.close()
