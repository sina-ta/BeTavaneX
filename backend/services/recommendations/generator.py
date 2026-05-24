from backend.services.recommendations.evaluators import (
    build_recommendation_payload,
    evaluate_rules,
)
from backend.services.recommendations.rules import (
    RecommendationContext,
)


def generate_recommendations(
    cpi: float,
    spi: float,
    progress_percent: float = 0.0,
    final_score: float = 0.0,
    risk_score: float = 0.0,
    workforce_count: int = 0,
) -> dict:
    context = RecommendationContext(
        cpi=cpi,
        spi=spi,
        progress_percent=progress_percent,
        final_score=final_score,
        risk_score=risk_score,
        workforce_count=workforce_count,
    )

    matched_rules = evaluate_rules(context)
    primary_rule = matched_rules[0]

    return build_recommendation_payload(primary_rule)


def generate_recommendation(
    cpi: float,
    spi: float,
) -> dict:
    """Backward-compatible single recommendation entry point."""
    return generate_recommendations(cpi=cpi, spi=spi)
