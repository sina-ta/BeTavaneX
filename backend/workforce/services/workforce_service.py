from backend.database import SessionLocal

from backend.models import DailyReport, DailyWorkOrder

from backend.workforce.repositories.worker_repository import (
    WorkerRepository,
    CrewRepository,
)
from backend.workforce.scoring.score_dimensions import (
    average_available_scores,
    build_score_snapshot,
)
from backend.workforce.validators.assignment_eligibility import (
    check_assignment_eligibility,
)
from backend.workforce.intelligence.daily_report_bridge import (
    summarize_daily_report_contribution,
)
from backend.workforce.analytics.operational_metrics import (
    compute_workforce_trend,
    build_crew_utilization,
)


def _serialize_worker_list_item(worker) -> dict:
    avg_score = average_available_scores(worker)

    return {
        "id": worker.id,
        "first_name": worker.first_name,
        "last_name": worker.last_name,
        "full_name": worker.full_name,
        "trade": worker.trade.name if worker.trade else "-",
        "current_role": worker.current_role,
        "crew": worker.crew.name if worker.crew else "-",
        "skill_level": worker.skill_level,
        "availability_status": worker.availability_status,
        "daily_cost": worker.daily_cost,
        "scores": build_score_snapshot(worker),
        "assignment_readiness": (
            "ready"
            if worker.availability_status == "available"
            else worker.availability_status
        ),
        "operational_score": avg_score,
        "is_active": worker.is_active,
    }


def list_workers_service() -> list[dict]:
    session = SessionLocal()

    try:
        repo = WorkerRepository(session)
        workers = repo.get_all_active()
        return [
            _serialize_worker_list_item(worker)
            for worker in workers
        ]
    finally:
        session.close()


def get_worker_detail_service(worker_id: int) -> dict:
    session = SessionLocal()

    try:
        repo = WorkerRepository(session)
        worker = repo.get_by_id(worker_id)

        if not worker:
            return {"error": "Worker not found"}

        item = _serialize_worker_list_item(worker)
        item.update({
            "phone": worker.phone,
            "current_project_id": worker.current_project_id,
            "safety_clearance": worker.safety_clearance,
            "skills": [
                ws.skill.name
                for ws in worker.skills
                if ws.skill
            ],
            "certifications": [
                wc.certification.name
                for wc in worker.certifications
                if wc.certification
            ],
        })
        return item
    finally:
        session.close()


def get_worker_intelligence_service(worker_id: int) -> dict:
    session = SessionLocal()

    try:
        repo = WorkerRepository(session)
        worker = repo.get_by_id(worker_id)

        if not worker:
            return {"error": "Worker not found"}

        reports = session.query(DailyReport).all()
        work_orders = session.query(DailyWorkOrder).all()
        assignments = repo.get_assignments(worker.id)
        attendance = repo.get_attendance(worker.id)

        daily_report_data = summarize_daily_report_contribution(
            worker.id,
            reports,
            work_orders,
        )

        attendance_rate = 0.0
        if attendance:
            present = len([
                record
                for record in attendance
                if record.status
                and record.status.lower() == "present"
            ])
            attendance_rate = round(
                (present / len(attendance)) * 100,
                2,
            )

        signals = []

        if daily_report_data["report_count"] == 0:
            signals.append({
                "signal": "daily_report_gap",
                "severity": "warning",
                "message": "No daily report contribution recorded yet",
            })
        else:
            signals.append({
                "signal": "daily_report_active",
                "severity": "stable",
                "message": f"{daily_report_data['report_count']} operational reports linked",
            })

        if daily_report_data["delay_events"] > 0:
            signals.append({
                "signal": "delay_contribution",
                "severity": "warning",
                "message": f"{daily_report_data['delay_events']} delay events in reports",
            })

        if attendance_rate and attendance_rate < 80:
            signals.append({
                "signal": "attendance",
                "severity": "warning",
                "message": "Attendance below operational target",
            })

        eligibility = check_assignment_eligibility(worker)

        return {
            "worker_id": worker.id,
            "full_name": worker.full_name,
            "trade": worker.trade.name if worker.trade else "-",
            "crew": worker.crew.name if worker.crew else "-",
            "availability_status": worker.availability_status,
            "scores": build_score_snapshot(worker),
            "operational_signals": signals,
            "daily_report_contribution": daily_report_data,
            "assignment_count": len(assignments),
            "attendance_rate": attendance_rate,
            "eligibility_summary": eligibility,
        }
    finally:
        session.close()


def get_workforce_analytics_service() -> dict:
    session = SessionLocal()

    try:
        worker_repo = WorkerRepository(session)
        crew_repo = CrewRepository(session)

        workers = worker_repo.get_all_active()
        crews = crew_repo.get_all()

        rows = [
            get_worker_intelligence_service(worker.id)
            for worker in workers
        ]

        productivity_scores = [
            row["scores"].get("productivity")
            for row in rows
            if row.get("scores")
        ]
        reliability_scores = [
            row["scores"].get("reliability")
            for row in rows
            if row.get("scores")
        ]

        available = len([
            worker
            for worker in workers
            if worker.availability_status == "available"
        ])
        assigned = len([
            worker
            for worker in workers
            if worker.availability_status == "assigned"
        ])

        avg_productivity = (
            round(
                sum(
                    score
                    for score in productivity_scores
                    if score is not None
                )
                / len([
                    score
                    for score in productivity_scores
                    if score is not None
                ]),
                2,
            )
            if any(
                score is not None
                for score in productivity_scores
            )
            else None
        )

        avg_reliability = (
            round(
                sum(
                    score
                    for score in reliability_scores
                    if score is not None
                )
                / len([
                    score
                    for score in reliability_scores
                    if score is not None
                ]),
                2,
            )
            if any(
                score is not None
                for score in reliability_scores
            )
            else None
        )

        return {
            "total_workers": len(workers),
            "available_workers": available,
            "assigned_workers": assigned,
            "avg_productivity_score": avg_productivity,
            "avg_reliability_score": avg_reliability,
            "crew_count": len(crews),
            "trend": compute_workforce_trend([
                average_available_scores(worker)
                for worker in workers
            ]),
            "workers": rows,
        }
    finally:
        session.close()


def list_crews_service() -> list[dict]:
    session = SessionLocal()

    try:
        crew_repo = CrewRepository(session)
        crews = crew_repo.get_all()

        return [
            {
                "id": crew.id,
                "name": crew.name,
                "trade": crew.trade,
                "supervisor": crew.supervisor,
                "active_project_id": crew.active_project_id,
                "performance_score": crew.performance_score,
                "utilization_rate": build_crew_utilization(
                    crew,
                    crew_repo.count_workers(crew.id),
                ),
                "worker_count": crew_repo.count_workers(crew.id),
            }
            for crew in crews
        ]
    finally:
        session.close()


def check_eligibility_service(
    worker_id: int,
    task_id: int | None = None,
) -> dict:
    session = SessionLocal()

    try:
        repo = WorkerRepository(session)
        worker = repo.get_by_id(worker_id)

        if not worker:
            return {"error": "Worker not found"}

        return check_assignment_eligibility(
            worker,
            task_id=task_id,
        )
    finally:
        session.close()
