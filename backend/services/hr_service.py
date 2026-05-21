from backend.database import SessionLocal

from backend.models.hr_models import (
    Worker
)


def get_workers_service():

    session = SessionLocal()

    workers = session.query(Worker).all()

    result = []

    for worker in workers:

        result.append({

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

            "status": worker.status
        })

    return result