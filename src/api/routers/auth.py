"""Auth routes: registration, login, and the current-user endpoint."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.config import settings
from api.core.db import get_db
from api.core.security import create_access_token
from api.dependencies import get_current_user
from api.models import User
from api.schemas import TokenResponse, UserCreate, UserLogin, UserRead
from api.services import user_service

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register(data: UserCreate, session: AsyncSession = Depends(get_db)) -> UserRead:
    """Create a new user account."""
    user = await user_service.create_user(session, data)
    return UserRead.model_validate(user)


@router.post("/login", response_model=TokenResponse)
async def login(data: UserLogin, session: AsyncSession = Depends(get_db)) -> TokenResponse:
    user = await user_service.authenticate_user(session, data.email, data.password)
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return TokenResponse(
        access_token=create_access_token(user.id),
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.get("/me", response_model=UserRead)
async def me(current_user: User = Depends(get_current_user)) -> UserRead:
    return UserRead.model_validate(current_user)
