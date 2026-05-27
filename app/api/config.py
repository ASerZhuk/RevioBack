import json
from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.models.app_config import AppConfig


router = APIRouter(prefix="/config", tags=["config"])


def _parse_value(raw: str) -> Any:
    try:
        return json.loads(raw)
    except Exception:
        return raw


@router.get("/app")
async def get_app_config(
    session: AsyncSession = Depends(get_db_session),
) -> dict[str, Any]:
    result = await session.execute(select(AppConfig))
    rows = result.scalars().all()
    return {
        row.key: "***" if row.is_secret else _parse_value(row.value)
        for row in rows
    }
