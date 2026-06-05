"""Event ledger dependency providers.

The event repository and recording service are built from the same
request-scoped Session as every other repository (via ``get_db``), so a recorded
event is committed in the same transaction as the operation it records.

Providers construct objects only; they never query, mutate, or compute.
"""

from __future__ import annotations

from fastapi import Depends
from sqlalchemy.orm import Session

from backend.db.session import get_db
from backend.phase1.events.event_recording_service import EventRecordingService
from backend.phase1.repositories.operational_event_repository import (
    OperationalEventRepository,
)


def get_operational_event_repository(
    session: Session = Depends(get_db),
) -> OperationalEventRepository:
    return OperationalEventRepository(session)


def get_event_recording_service(
    event_repository: OperationalEventRepository = Depends(
        get_operational_event_repository,
    ),
) -> EventRecordingService:
    return EventRecordingService(event_repository)
