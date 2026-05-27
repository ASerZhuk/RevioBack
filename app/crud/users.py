import json

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import hash_password, verify_password
from app.models.user import User


async def _get_initial_tokens(session: AsyncSession) -> int:
    from app.models.app_config import AppConfig
    row = await session.get(AppConfig, "app.initial_user_tokens")
    if row is not None:
        try:
            return int(json.loads(row.value))
        except Exception:
            pass
    return settings.initial_user_tokens


async def get_user_by_id(session: AsyncSession, user_id: int) -> User | None:
    return await session.get(User, user_id)


async def get_user_by_username(session: AsyncSession, username: str) -> User | None:
    result = await session.execute(select(User).where(User.username == username))
    return result.scalar_one_or_none()


async def get_user_by_google_sub(session: AsyncSession, google_sub: str) -> User | None:
    result = await session.execute(select(User).where(User.google_sub == google_sub))
    return result.scalar_one_or_none()


async def get_user_by_email(session: AsyncSession, email: str) -> User | None:
    result = await session.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def get_user_by_device_id(session: AsyncSession, device_id: str) -> User | None:
    result = await session.execute(select(User).where(User.device_id == device_id))
    return result.scalar_one_or_none()


async def create_user(session: AsyncSession, username: str, password: str, device_id: str | None = None) -> User:
    user = User(
        username=username,
        email=username,
        password_hash=hash_password(password),
        auth_provider="password",
        tokens=await _get_initial_tokens(session),
        device_id=device_id,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def create_google_user(
    session: AsyncSession,
    email: str,
    google_sub: str,
    device_id: str | None = None,
) -> User:
    user = User(
        username=email,
        email=email,
        google_sub=google_sub,
        auth_provider="google",
        tokens=await _get_initial_tokens(session),
        device_id=device_id,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def attach_google_to_user(
    session: AsyncSession,
    user: User,
    email: str,
    google_sub: str,
) -> User:
    user.email = email
    user.google_sub = google_sub
    user.auth_provider = "google"
    await session.commit()
    await session.refresh(user)
    return user


async def authenticate_user(
    session: AsyncSession,
    username: str,
    password: str,
) -> User | None:
    user = await get_user_by_username(session, username)
    if user is None or user.password_hash is None or not verify_password(password, user.password_hash):
        return None

    return user
