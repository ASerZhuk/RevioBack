# Import SQLAlchemy models here so Alembic can detect metadata changes.
from app.models.analysis_history import AnalysisHistory
from app.models.user import User

__all__ = ["AnalysisHistory", "User"]
