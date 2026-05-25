from backend.workforce.scoring.score_dimensions import (
    average_available_scores,
)


def compute_workforce_trend(scores: list[float | None]) -> str:
    values = [score for score in scores if score is not None]

    if len(values) < 2:
        return "stable"

    midpoint = len(values) // 2
    first_half = values[:midpoint] or values[:1]
    second_half = values[midpoint:] or values[-1:]

    first_avg = sum(first_half) / len(first_half)
    second_avg = sum(second_half) / len(second_half)

    if second_avg > first_avg + 2:
        return "improving"

    if second_avg < first_avg - 2:
        return "declining"

    return "stable"


def build_crew_utilization(crew, worker_count: int) -> float | None:
    if crew.utilization_rate is not None:
        return crew.utilization_rate

    if worker_count <= 0:
        return 0.0

    return round(min(worker_count * 10, 100), 2)
