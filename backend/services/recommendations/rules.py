from dataclasses import dataclass, field
from typing import Callable


@dataclass
class RecommendationContext:
    cpi: float
    spi: float
    progress_percent: float = 0.0
    final_score: float = 0.0
    risk_score: float = 0.0
    workforce_count: int = 0
    budget_variance: float = 0.0


@dataclass
class RecommendationRule:
    rule_id: str
    title: str
    action: str
    severity: str
    factors: list[str]
    condition: Callable[[RecommendationContext], bool]
    explanation: str


RECOMMENDATION_RULES: list[RecommendationRule] = [
    RecommendationRule(
        rule_id="schedule_delay",
        title="Schedule Delay",
        action="Increase manpower to recover lost schedule progress",
        severity="warning",
        factors=["schedule"],
        condition=lambda ctx: ctx.spi < 1 and ctx.cpi >= 1,
        explanation=(
            "Schedule performance index is below target "
            "while cost performance remains stable."
        ),
    ),
    RecommendationRule(
        rule_id="critical_risk",
        title="Critical Risk",
        action="Review workforce allocation and cost controls immediately",
        severity="critical",
        factors=["schedule", "budget", "workforce"],
        condition=lambda ctx: ctx.spi < 1 and ctx.cpi < 1,
        explanation=(
            "Both schedule and budget indicators are under pressure."
        ),
    ),
    RecommendationRule(
        rule_id="cost_overrun",
        title="Cost Overrun",
        action="Reduce unnecessary costs and validate resource usage",
        severity="warning",
        factors=["budget"],
        condition=lambda ctx: ctx.spi >= 1 and ctx.cpi < 1,
        explanation=(
            "Schedule is on track but spending efficiency is declining."
        ),
    ),
    RecommendationRule(
        rule_id="workforce_pressure",
        title="Workforce Pressure",
        action="Rebalance crew assignments and monitor attendance",
        severity="warning",
        factors=["workforce", "schedule"],
        condition=lambda ctx: (
            ctx.workforce_count > 0
            and ctx.spi < 0.9
            and ctx.workforce_count < 5
        ),
        explanation=(
            "Schedule delay detected with limited active manpower."
        ),
    ),
    RecommendationRule(
        rule_id="project_stable",
        title="Project Stable",
        action="Maintain current performance and monitor trends",
        severity="stable",
        factors=["schedule", "budget"],
        condition=lambda ctx: ctx.spi >= 1 and ctx.cpi >= 1,
        explanation=(
            "Schedule and budget indicators are within operational targets."
        ),
    ),
]
