from dataclasses import dataclass, field
from typing import Any, Callable, Optional

from backend.validation.utils.enums import (
    ValidationSeverity,
    ValidationTarget,
)


@dataclass
class ValidationFinding:
    rule_id: str
    target: ValidationTarget
    severity: ValidationSeverity
    passed: bool
    message: str
    explanation: str
    confidence: float = 0.85
    affected_entities: dict[str, Any] = field(default_factory=dict)
    operational_impact: str = ""


@dataclass
class ValidationContext:
    """Operational context passed to all validation rules."""
    report_payload: Any
    work_order: Any | None
    work_order_reports: list[Any] = field(default_factory=list)
    all_reports: list[Any] = field(default_factory=list)
    related_attendance: list[Any] = field(default_factory=list)


ValidationRuleFn = Callable[
    [ValidationContext],
    Optional[ValidationFinding],
]


@dataclass
class RegisteredRule:
    rule_id: str
    name: str
    target: ValidationTarget
    evaluate: ValidationRuleFn
