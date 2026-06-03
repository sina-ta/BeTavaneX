"""Delete guards to prevent orphan operational data via repository deletes."""

from __future__ import annotations

# Junction / mapping rows may be removed during execution corrections.
_DELETE_ALLOWED_MODELS = {
    "WorkOrderWorkflowStep",
    "BOQMapping",
}


def assert_delete_allowed(model: type) -> None:
    name = model.__name__
    if name in _DELETE_ALLOWED_MODELS:
        return
    msg = (
        f"Delete blocked for {name}: Phase 1 uses RESTRICT FKs; "
        "remove via controlled cascade paths only."
    )
    raise ValueError(msg)
