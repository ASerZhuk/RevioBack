from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class AnalysisHistory(Base):
    __tablename__ = "analysis_history"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    source: Mapped[str] = mapped_column(String(32))
    product_url: Mapped[str] = mapped_column(Text)
    product_title: Mapped[str | None] = mapped_column(String(512))
    product_price: Mapped[str | None] = mapped_column(String(128))
    summary: Mapped[str] = mapped_column(Text)
    pros: Mapped[str] = mapped_column(Text)
    cons: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
