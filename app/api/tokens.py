from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db_session
from app.models.user import User
from app.schemas.auth import UserRead


router = APIRouter(prefix="/tokens", tags=["tokens"])


@router.post("/consume-analysis", response_model=UserRead)
async def consume_analysis_token(
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> User:
    if current_user.tokens <= 0:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Недостаточно токенов для анализа.",
        )

    current_user.tokens -= 1
    await session.commit()
    await session.refresh(current_user)
    return current_user


@router.post("/refund-analysis", response_model=UserRead)
async def refund_analysis_token(
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> User:
    current_user.tokens += 1
    await session.commit()
    await session.refresh(current_user)
    return current_user


@router.post("/rewarded", response_model=UserRead)
async def reward_rewarded_token(
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> User:
    current_user.tokens += 5
    await session.commit()
    await session.refresh(current_user)
    return current_user
