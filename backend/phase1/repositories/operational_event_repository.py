"""Append-only repository for the operational event ledger.

This repository deliberately does NOT extend ``BaseRepository``: the ledger
supports only append + read. ``update`` and ``delete`` are not provided, and the
explicit guards below make the immutability contract a hard error rather than a
convention.
"""

from __future__ import annotations

from typing import NoReturn
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.phase1.models.operational_event import OperationalEvent


class EventLedgerImmutabilityError(RuntimeError):
    """Raised on any attempt to mutate or remove a persisted operational event."""


class OperationalEventRepository:
    """Append-only persistence for ``operational_events`` (no update, no delete)."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def append(self, event: OperationalEvent) -> OperationalEvent:
        """Persist a new event. The only write path into the ledger."""
        self._session.add(event)
        self._session.flush()
        self._session.refresh(event)
        return event

    def get_by_id(self, event_id: UUID) -> OperationalEvent | None:
        return self._session.get(OperationalEvent, event_id)

    def list_for_aggregate(
        self,
        aggregate_type: str,
        aggregate_id: UUID,
        *,
        offset: int = 0,
        limit: int = 200,
    ) -> list[OperationalEvent]:
        statement = (
            select(OperationalEvent)
            .where(OperationalEvent.aggregate_type == aggregate_type)
            .where(OperationalEvent.aggregate_id == aggregate_id)
            .order_by(OperationalEvent.occurred_at.asc())
            .offset(offset)
            .limit(limit)
        )
        return list(self._session.scalars(statement).all())

    def list_by_type(
        self,
        event_type: str,
        *,
        offset: int = 0,
        limit: int = 200,
    ) -> list[OperationalEvent]:
        statement = (
            select(OperationalEvent)
            .where(OperationalEvent.event_type == event_type)
            .order_by(OperationalEvent.occurred_at.desc())
            .offset(offset)
            .limit(limit)
        )
        return list(self._session.scalars(statement).all())

    # --- Immutability guards ---------------------------------------------------
    # The ledger has no update or delete semantics. These exist so that any
    # accidental call fails loudly instead of silently mutating lineage.

    def update(self, *_args: object, **_kwargs: object) -> NoReturn:
        raise EventLedgerImmutabilityError(
            "operational_events is append-only; events cannot be updated.",
        )

    def delete(self, *_args: object, **_kwargs: object) -> NoReturn:
        raise EventLedgerImmutabilityError(
            "operational_events is append-only; events cannot be deleted.",
        )
