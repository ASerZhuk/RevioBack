"""add device_id to users

Revision ID: 20260527_0009
Revises: 20260527_0008
Create Date: 2026-05-27

"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "20260527_0009"
down_revision: str | Sequence[str] | None = "20260527_0008"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("users", sa.Column("device_id", sa.String(255), nullable=True))
    op.create_index(op.f("ix_users_device_id"), "users", ["device_id"], unique=True)


def downgrade() -> None:
    op.drop_index(op.f("ix_users_device_id"), table_name="users")
    op.drop_column("users", "device_id")
