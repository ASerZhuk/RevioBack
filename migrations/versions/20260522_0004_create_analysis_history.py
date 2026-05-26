"""create analysis history

Revision ID: 20260522_0004
Revises: 20260522_0003
Create Date: 2026-05-22

"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "20260522_0004"
down_revision: str | Sequence[str] | None = "20260522_0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "analysis_history",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("source", sa.String(length=32), nullable=False),
        sa.Column("product_url", sa.Text(), nullable=False),
        sa.Column("product_title", sa.String(length=512), nullable=True),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("pros", sa.Text(), nullable=False),
        sa.Column("cons", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_analysis_history_id"), "analysis_history", ["id"], unique=False)
    op.create_index(op.f("ix_analysis_history_user_id"), "analysis_history", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_analysis_history_user_id"), table_name="analysis_history")
    op.drop_index(op.f("ix_analysis_history_id"), table_name="analysis_history")
    op.drop_table("analysis_history")
