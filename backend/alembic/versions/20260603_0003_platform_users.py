"""Platform users table for persisted IAM.

Revision ID: 20260603_0003
Revises: 20260603_0002
Create Date: 2026-06-03
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "20260603_0003"
down_revision: Union[str, None] = "20260603_0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "platform_users",
        sa.Column("username", sa.String(length=150), nullable=False),
        sa.Column("role", sa.String(length=32), nullable=False),
        sa.Column("hashed_password", sa.String(length=512), nullable=False),
        sa.Column("disabled", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("username"),
        if_not_exists=True,
    )
    op.create_index(
        "idx_platform_users_username",
        "platform_users",
        ["username"],
        unique=True,
        if_not_exists=True,
    )
    op.create_index(
        "idx_platform_users_role",
        "platform_users",
        ["role"],
        if_not_exists=True,
    )


def downgrade() -> None:
    op.drop_index("idx_platform_users_role", table_name="platform_users")
    op.drop_index("idx_platform_users_username", table_name="platform_users")
    op.drop_table("platform_users")
