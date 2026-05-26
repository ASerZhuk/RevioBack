import json
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db_session
from app.models.analysis_history import AnalysisHistory
from app.models.user import User
from app.schemas.history import AnalysisHistoryCreate, AnalysisHistoryPriceUpdate, AnalysisHistoryRead


router = APIRouter(prefix="/history", tags=["history"])


def serialize_history(item: AnalysisHistory) -> AnalysisHistoryRead:
    return AnalysisHistoryRead(
        id=item.id,
        source=item.source,
        product_url=item.product_url,
        product_title=item.product_title,
        product_price=item.product_price,
        summary=item.summary,
        pros=json.loads(item.pros),
        cons=json.loads(item.cons),
        created_at=item.created_at,
    )


@router.get("", response_model=list[AnalysisHistoryRead])
async def list_history(
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> list[AnalysisHistoryRead]:
    result = await session.execute(
        select(AnalysisHistory)
        .where(AnalysisHistory.user_id == current_user.id)
        .order_by(AnalysisHistory.created_at.desc(), AnalysisHistory.id.desc())
    )
    return [serialize_history(item) for item in result.scalars().all()]


@router.post("", response_model=AnalysisHistoryRead)
async def create_history_item(
    payload: AnalysisHistoryCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> AnalysisHistoryRead:
    item = AnalysisHistory(
        user_id=current_user.id,
        source=payload.source,
        product_url=payload.product_url,
        product_title=payload.product_title,
        product_price=payload.product_price,
        summary=payload.summary,
        pros=json.dumps(payload.pros, ensure_ascii=False),
        cons=json.dumps(payload.cons, ensure_ascii=False),
    )
    session.add(item)
    await session.commit()
    await session.refresh(item)
    return serialize_history(item)


@router.patch("/{history_id}", response_model=AnalysisHistoryRead)
async def update_history_price(
    history_id: int,
    payload: AnalysisHistoryPriceUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> AnalysisHistoryRead:
    result = await session.execute(
        select(AnalysisHistory).where(
            AnalysisHistory.id == history_id,
            AnalysisHistory.user_id == current_user.id,
        )
    )
    item = result.scalar_one_or_none()

    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="History item not found")

    item.product_price = payload.product_price
    await session.commit()
    await session.refresh(item)

    return serialize_history(item)


@router.delete("/{history_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_history_item(
    history_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> None:
    result = await session.execute(
        select(AnalysisHistory).where(
            AnalysisHistory.id == history_id,
            AnalysisHistory.user_id == current_user.id,
        )
    )
    item = result.scalar_one_or_none()

    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="History item not found")

    await session.delete(item)
    await session.commit()
