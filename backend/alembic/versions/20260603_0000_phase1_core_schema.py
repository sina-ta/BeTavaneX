"""Phase 1 core ORM schema (all tables) — Alembic-owned greenfield bootstrap.

Revision ID: 20260603_0000
Revises:
Create Date: 2026-06-03

Docker and production use ``alembic upgrade head`` only. This revision applies
``Base.metadata.create_all(checkfirst=True)`` once. Later revisions add indexes
and tables with ``if_not_exists`` where they may overlap ORM metadata.

Manual dev bootstrap (optional): ``python backend/scripts/phase1_init_schema.py``
"""

from typing import Sequence, Union

from alembic import op

revision: str = "20260603_0000"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    import backend.phase1.models  # noqa: F401 — register metadata
    from backend.db.base import Base

    bind = op.get_bind()
    Base.metadata.create_all(bind=bind, checkfirst=True)


def downgrade() -> None:
    # Intentional no-op: dropping the full Phase 1 schema is destructive and
    # not required for rolling back incremental revisions.
    pass
