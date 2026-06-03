"""Phase 1 application exceptions."""

from __future__ import annotations


class ConcurrencyConflictError(Exception):
    """Raised when optimistic lock token (updated_at) does not match persisted row."""

    def __init__(self, resource_type: str, resource_id: str) -> None:
        self.resource_type = resource_type
        self.resource_id = resource_id
        super().__init__(
            f"Concurrent update conflict on {resource_type} {resource_id}",
        )
