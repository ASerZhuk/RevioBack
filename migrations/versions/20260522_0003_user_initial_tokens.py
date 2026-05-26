"""user initial tokens

Revision ID: 20260522_0003
Revises: 20260522_0002
Create Date: 2026-05-22

"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "20260522_0003"
down_revision: str | Sequence[str] | None = "20260522_0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.batch_alter_table("users") as batch_op:
        batch_op.alter_column(
            "tokens",
            existing_type=sa.Integer(),
            server_default="3",
            existing_nullable=False,
        )


def downgrade() -> None:
    with op.batch_alter_table("users") as batch_op:
        batch_op.alter_column(
            "tokens",
            existing_type=sa.Integer(),
            server_default="0",
            existing_nullable=False,
        )
