"""Readiness authority boundaries — derived readiness is not directly writable."""

from __future__ import annotations


class ReadinessAuthorityError(ValueError):
    """Raised when a caller attempts to assert readiness outside the deriver."""


def reject_direct_ready_mutation(
    requested_ready: bool | None,
    *,
    context: str = "workflow_step",
) -> None:
    """Block direct readiness assertions.

    ``False`` and ``None`` are permitted (default / non-assertion). ``True`` is
    rejected because readiness must be derived from operational evidence.
    """
    if requested_ready is True:
        msg = (
            f"Readiness for {context} cannot be set directly; "
            "it is derived by ReadinessDerivationService from blockers, "
            "dependencies, and workflow state."
        )
        raise ReadinessAuthorityError(msg)
