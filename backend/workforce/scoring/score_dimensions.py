"""Modular operational score dimensions.

Scores are derived from daily reports and field operations,
never manually hardcoded in production flows.
"""

from backend.workforce.utils.enums import ScoreDimension

SCORE_DIMENSIONS = [
    ScoreDimension.PRODUCTIVITY,
    ScoreDimension.RELIABILITY,
    ScoreDimension.QUALITY,
    ScoreDimension.SAFETY,
    ScoreDimension.TEAMWORK,
    ScoreDimension.DISCIPLINE,
    ScoreDimension.LEADERSHIP,
]

WORKER_SCORE_FIELDS = {
    ScoreDimension.PRODUCTIVITY: "productivity_score",
    ScoreDimension.RELIABILITY: "reliability_score",
    ScoreDimension.QUALITY: "quality_score",
    ScoreDimension.SAFETY: "safety_score",
    ScoreDimension.TEAMWORK: "teamwork_score",
    ScoreDimension.DISCIPLINE: "reliability_score",
    ScoreDimension.LEADERSHIP: "leadership_score",
}


def build_score_snapshot(worker) -> dict:
    return {
        dimension.value: getattr(
            worker,
            WORKER_SCORE_FIELDS[dimension],
            None,
        )
        for dimension in SCORE_DIMENSIONS
    }


def average_available_scores(worker) -> float | None:
    values = [
        getattr(worker, field)
        for field in {
            "productivity_score",
            "reliability_score",
            "quality_score",
            "safety_score",
            "teamwork_score",
            "leadership_score",
        }
        if getattr(worker, field) is not None
    ]

    if not values:
        return None

    return round(sum(values) / len(values), 2)
