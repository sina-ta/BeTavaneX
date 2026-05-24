from backend.services.recommendations.rules import (
    RECOMMENDATION_RULES,
    RecommendationContext,
    RecommendationRule,
)


def evaluate_rules(
    context: RecommendationContext,
) -> list[RecommendationRule]:
    matched = [
        rule
        for rule in RECOMMENDATION_RULES
        if rule.condition(context)
    ]

    if matched:
        return matched

    return [
        rule
        for rule in RECOMMENDATION_RULES
        if rule.rule_id == "project_stable"
    ]


def build_recommendation_payload(
    rule: RecommendationRule,
) -> dict:
    return {
        "title": rule.title,
        "action": rule.action,
        "severity": rule.severity,
        "factors": rule.factors,
        "explanation": rule.explanation,
        "rule_id": rule.rule_id,
    }
