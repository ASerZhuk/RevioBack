import json
from datetime import datetime
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_admin_user
from app.db.session import get_db_session
from app.models.analysis_history import AnalysisHistory
from app.models.app_config import AppConfig
from app.models.error_log import ErrorLog
from app.models.user import User


router = APIRouter(prefix="/admin", tags=["admin"])

AdminUser = Annotated[User, Depends(get_admin_user)]
DB = Annotated[AsyncSession, Depends(get_db_session)]


# --- schemas ---

class UserUpdate(BaseModel):
    tokens: int | None = None
    is_admin: bool | None = None


class ConfigUpdate(BaseModel):
    value: Any
    description: str | None = None


class UserOut(BaseModel):
    id: int
    username: str
    email: str | None
    tokens: int
    is_admin: bool
    auth_provider: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ConfigOut(BaseModel):
    key: str
    value: Any
    description: str
    is_secret: bool
    updated_at: datetime

    model_config = {"from_attributes": True}


class ErrorOut(BaseModel):
    id: int
    source: str
    error_type: str
    message: str
    context: str | None
    user_id: int | None
    resolved: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# --- dashboard ---

@router.get("/dashboard")
async def dashboard(_: AdminUser, session: DB) -> dict:
    total_users = (await session.execute(select(func.count()).select_from(User))).scalar_one()
    total_analyses = (await session.execute(select(func.count()).select_from(AnalysisHistory))).scalar_one()
    total_errors = (await session.execute(select(func.count()).select_from(ErrorLog))).scalar_one()
    unresolved_errors = (await session.execute(
        select(func.count()).select_from(ErrorLog).where(ErrorLog.resolved == False)  # noqa: E712
    )).scalar_one()

    return {
        "total_users": total_users,
        "total_analyses": total_analyses,
        "total_errors": total_errors,
        "unresolved_errors": unresolved_errors,
    }


# --- users ---

@router.get("/users", response_model=list[UserOut])
async def list_users(_: AdminUser, session: DB) -> list[User]:
    result = await session.execute(select(User).order_by(User.id))
    return list(result.scalars().all())


@router.patch("/users/{user_id}", response_model=UserOut)
async def update_user(user_id: int, payload: UserUpdate, _: AdminUser, session: DB) -> User:
    user = await session.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if payload.tokens is not None:
        user.tokens = payload.tokens
    if payload.is_admin is not None:
        user.is_admin = payload.is_admin

    await session.commit()
    await session.refresh(user)
    return user


@router.delete("/users/{user_id}", status_code=204)
async def delete_user(user_id: int, current_admin: AdminUser, session: DB) -> None:
    user = await session.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if user.id == current_admin.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot delete yourself")

    await session.delete(user)
    await session.commit()


# --- config ---

def _parse_value(raw: str) -> Any:
    try:
        return json.loads(raw)
    except Exception:
        return raw


def _config_out(row: AppConfig) -> dict:
    return {
        "key": row.key,
        "value": "***" if row.is_secret else _parse_value(row.value),
        "description": row.description,
        "is_secret": row.is_secret,
        "updated_at": row.updated_at,
    }


@router.get("/config")
async def list_config(_: AdminUser, session: DB) -> list[dict]:
    result = await session.execute(select(AppConfig).order_by(AppConfig.key))
    return [_config_out(row) for row in result.scalars().all()]


@router.put("/config/{key:path}")
async def update_config(key: str, payload: ConfigUpdate, _: AdminUser, session: DB) -> dict:
    row = await session.get(AppConfig, key)
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Config key '{key}' not found")

    from datetime import datetime, timezone
    row.value = json.dumps(payload.value, ensure_ascii=False)
    row.updated_at = datetime.now(timezone.utc)
    if payload.description is not None:
        row.description = payload.description

    await session.commit()
    await session.refresh(row)
    return _config_out(row)


# --- errors ---

@router.get("/errors", response_model=list[ErrorOut])
async def list_errors(_: AdminUser, session: DB, resolved: bool | None = None) -> list[ErrorLog]:
    q = select(ErrorLog).order_by(ErrorLog.created_at.desc())
    if resolved is not None:
        q = q.where(ErrorLog.resolved == resolved)
    result = await session.execute(q)
    return list(result.scalars().all())


@router.post("/errors/{error_id}/resolve", response_model=ErrorOut)
async def resolve_error(error_id: int, _: AdminUser, session: DB) -> ErrorLog:
    log = await session.get(ErrorLog, error_id)
    if log is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Error log not found")

    log.resolved = True
    await session.commit()
    await session.refresh(log)
    return log
