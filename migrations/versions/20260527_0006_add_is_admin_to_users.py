"""add is_admin to users

Revision ID: 20260527_0006
Revises: 20260525_0005
Create Date: 2026-05-27

"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text


revision: str = "20260527_0006"
down_revision: str | Sequence[str] | None = "20260525_0005"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    conn = op.get_bind()
    columns = {row[1] for row in conn.execute(text("PRAGMA table_info(users)"))}
    if "is_admin" not in columns:
        op.add_column("users", sa.Column("is_admin", sa.Boolean(), server_default="0", nullable=False))


def downgrade() -> None:
    op.drop_column("users", "is_admin")
