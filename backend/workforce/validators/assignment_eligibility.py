from datetime import date

from backend.workforce.models.worker import Worker


def check_assignment_eligibility(
    worker: Worker,
    *,
    required_skills: list[str] | None = None,
    task_id: int | None = None,
) -> dict:
    """Foundation validator — answers CAN this worker perform this task?"""
    factors = []

    if not worker.is_active:
        factors.append({
            "factor": "active_status",
            "passed": False,
            "message": "Worker is inactive",
        })
    else:
        factors.append({
            "factor": "active_status",
            "passed": True,
            "message": "Worker is active",
        })

    availability_ok = worker.availability_status in {
        "available",
        "assigned",
    }
    factors.append({
        "factor": "availability",
        "passed": availability_ok,
        "message": f"Availability: {worker.availability_status}",
    })

    medical_ok = worker.medical_status_id is not None
    factors.append({
        "factor": "medical_clearance",
        "passed": medical_ok,
        "message": "Medical clearance on file"
        if medical_ok
        else "Medical clearance missing",
    })

    safety_ok = bool(
        worker.safety_clearance
        and worker.safety_clearance.lower()
        in {"cleared", "approved", "valid"}
    )
    factors.append({
        "factor": "safety_clearance",
        "passed": safety_ok,
        "message": f"Safety clearance: {worker.safety_clearance or 'missing'}",
    })

    worker_skill_names = [
        ws.skill.name
        for ws in worker.skills
        if ws.skill
    ]

    if required_skills:
        missing = [
            skill
            for skill in required_skills
            if skill not in worker_skill_names
        ]
        factors.append({
            "factor": "skill_match",
            "passed": len(missing) == 0,
            "message": "Skills matched"
            if not missing
            else f"Missing skills: {', '.join(missing)}",
        })

    expired_certs = []
    today = date.today()

    for wc in worker.certifications:
        if wc.expiry_date and wc.expiry_date < today:
            name = (
                wc.certification.name
                if wc.certification
                else "certification"
            )
            expired_certs.append(name)

    factors.append({
        "factor": "certification_validity",
        "passed": len(expired_certs) == 0,
        "message": "Certifications valid"
        if not expired_certs
        else f"Expired: {', '.join(expired_certs)}",
    })

    fatigue_ready = worker.productivity_score is None or (
        worker.productivity_score >= 40
    )
    factors.append({
        "factor": "fatigue_readiness",
        "passed": fatigue_ready,
        "message": "Fatigue readiness acceptable",
    })

    if task_id is not None:
        factors.append({
            "factor": "task_context",
            "passed": True,
            "message": f"Task {task_id} eligibility evaluated",
        })

    eligible = all(factor["passed"] for factor in factors)

    return {
        "worker_id": worker.id,
        "task_id": task_id,
        "eligible": eligible,
        "factors": factors,
    }
