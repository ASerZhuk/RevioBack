"""add product price to analysis history

Revision ID: 20260525_0005
Revises: 20260522_0004
Create Date: 2026-05-25

"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text


revision: str = "20260525_0005"
down_revision: str | Sequence[str] | None = "20260522_0004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    conn = op.get_bind()
    columns = {row[1] for row in conn.execute(text("PRAGMA table_info(analysis_history)"))}

    if "product_price" not in columns:
        op.add_column(
            "analysis_history",
            sa.Column("product_price", sa.String(length=128), nullable=True),
        )


def downgrade() -> None:
    op.drop_column("analysis_history", "product_price")
