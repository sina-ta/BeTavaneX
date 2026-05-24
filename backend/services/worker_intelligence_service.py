from backend.database import SessionLocal

from backend.repositories.worker_repository import (
    WorkerRepository,
)

from backend.services.analytics_service import (
    calculate_trend,
)


def _attendance_rate(attendance_records) -> float:
    if not attendance_records:
        return 0.0

    present_count = len([
        record
        for record in attendance_records
        if record.status and record.status.lower() == "present"
    ])

    return round(
        (present_count / len(attendance_records)) * 100,
        2,
    )


def _productivity_score(attendance_records) -> float:
    if not attendance_records:
        return 0.0

    total_hours = sum(
        record.work_hours or 0
        for record in attendance_records
    )

    return round(
        min(total_hours / len(attendance_records), 10) * 10,
        2,
    )


def _build_worker_intelligence(
    repo: WorkerRepository,
    worker,
) -> dict:
    attendance = repo.get_attendance_by_worker_id(worker.id)
    score_record = repo.get_latest_score_by_worker_id(worker.id)
    assignments = repo.get_assignments_by_worker_id(worker.id)

    attendance_rate = _attendance_rate(attendance)
    productivity_score = _productivity_score(attendance)

    if score_record:
        operational_score = round(score_record.final_score, 2)
    else:
        operational_score = round(
            (attendance_rate * 0.4)
            + (productivity_score * 0.6),
            2,
        )

    crew_efficiency = operational_score

    if worker.crew_id:
        crew_worker_ids = repo.get_crew_worker_ids(
            worker.crew_id,
        )

        crew_scores = []

        for crew_worker_id in crew_worker_ids:
            crew_score = repo.get_latest_score_by_worker_id(
                crew_worker_id,
            )

            if crew_score:
                crew_scores.append(crew_score.final_score)

        if crew_scores:
            crew_efficiency = round(
                sum(crew_scores) / len(crew_scores),
                2,
            )

    factors = []

    if attendance_rate < 80:
        factors.append({
            "factor": "attendance",
            "status": "warning",
            "message": "Attendance rate is below target",
        })

    if productivity_score < 60:
        factors.append({
            "factor": "productivity",
            "status": "warning",
            "message": "Productivity score needs improvement",
        })

    if operational_score >= 80:
        factors.append({
            "factor": "performance",
            "status": "stable",
            "message": "Worker performance is stable",
        })

    return {
        "worker_id": worker.id,
        "full_name": worker.full_name,
        "role": worker.role.title if worker.role else "-",
        "crew": worker.crew.name if worker.crew else "-",
        "attendance_rate": attendance_rate,
        "productivity_score": productivity_score,
        "crew_efficiency": crew_efficiency,
        "operational_score": operational_score,
        "skill_performance": {
            "productivity": score_record.productivity_score
            if score_record
            else productivity_score,
            "quality": score_record.quality_score
            if score_record
            else 0,
            "safety": score_record.safety_score
            if score_record
            else 0,
            "discipline": score_record.discipline_score
            if score_record
            else 0,
        },
        "assignment_count": len(assignments),
        "factors": factors,
    }


def get_worker_intelligence_service(worker_id: int) -> dict:
    session = SessionLocal()

    try:
        repo = WorkerRepository(session)
        worker = repo.get_by_id(worker_id)

        if not worker:
            return {"error": "Worker not found"}

        return _build_worker_intelligence(repo, worker)

    finally:
        session.close()


def get_workforce_analytics_service() -> dict:
    session = SessionLocal()

    try:
        repo = WorkerRepository(session)
        workers = repo.get_all()

        if not workers:
            return {
                "total_workers": 0,
                "avg_operational_score": 0,
                "avg_attendance_rate": 0,
                "trend": "stable",
                "workers": [],
            }

        intelligence_rows = []
        scores = []
        attendance_rates = []

        for worker in workers:
            row = _build_worker_intelligence(repo, worker)
            intelligence_rows.append(row)
            scores.append(row["operational_score"])
            attendance_rates.append(row["attendance_rate"])

        return {
            "total_workers": len(intelligence_rows),
            "avg_operational_score": round(
                sum(scores) / len(scores),
                2,
            )
            if scores
            else 0,
            "avg_attendance_rate": round(
                sum(attendance_rates) / len(attendance_rates),
                2,
            )
            if attendance_rates
            else 0,
            "trend": calculate_trend(scores),
            "workers": intelligence_rows,
        }

    finally:
        session.close()
