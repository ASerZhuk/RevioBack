import json
from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.telegram import notify_error
from app.db.session import get_db_session
from app.models.error_log import ErrorLog
from app.models.user import User


router = APIRouter(prefix="/errors", tags=["errors"])


class ErrorReport(BaseModel):
    error_type: str = ""
    message: str
    context: dict | None = None


@router.post("/report", status_code=204)
async def report_error(
    payload: ErrorReport,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> None:
    ctx = json.dumps(payload.context, ensure_ascii=False) if payload.context else None
    log = ErrorLog(
        source="mobile",
        error_type=payload.error_type,
        message=payload.message,
        context=ctx,
        user_id=current_user.id,
    )
    session.add(log)
    await session.commit()
    await notify_error("mobile", payload.error_type, payload.message, ctx)
