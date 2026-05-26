from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.google_auth import verify_google_id_token
from app.core.security import create_access_token
from app.crud.users import (
    attach_google_to_user,
    authenticate_user,
    create_google_user,
    create_user,
    get_user_by_email,
    get_user_by_google_sub,
    get_user_by_username,
)
from app.db.session import get_db_session
from app.models.user import User
from app.schemas.auth import GoogleLogin, TokenResponse, UserCreate, UserLogin, UserRead


router = APIRouter(prefix="/auth", tags=["auth"])


def build_token_response(user: User) -> TokenResponse:
    return TokenResponse(access_token=create_access_token(user.id), user=user)


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    payload: UserCreate,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> TokenResponse:
    existing_user = await get_user_by_username(session, payload.username)
    if existing_user is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already exists")

    user = await create_user(session, payload.username, payload.password)
    return build_token_response(user)


@router.post("/login", response_model=TokenResponse)
async def login(
    payload: UserLogin,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> TokenResponse:
    user = await authenticate_user(session, payload.username, payload.password)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")

    return build_token_response(user)


@router.post("/google", response_model=TokenResponse)
async def google_login(
    payload: GoogleLogin,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> TokenResponse:
    google_user = await verify_google_id_token(payload.id_token)
    if google_user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Google token")

    email, google_sub = google_user
    user = await get_user_by_google_sub(session, google_sub)
    if user is not None:
        return build_token_response(user)

    user = await get_user_by_email(session, email)
    if user is not None:
        user = await attach_google_to_user(session, user, email, google_sub)
        return build_token_response(user)

    user = await get_user_by_username(session, email)
    if user is not None:
        user = await attach_google_to_user(session, user, email, google_sub)
        return build_token_response(user)

    user = await create_google_user(session, email, google_sub)
    return build_token_response(user)


@router.get("/me", response_model=UserRead)
async def me(current_user: Annotated[User, Depends(get_current_user)]) -> User:
    return current_user
