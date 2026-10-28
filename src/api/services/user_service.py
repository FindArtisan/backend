"""User account operations (registration, authentication lookup)."""

import uuid

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.security import hash_password, verify_password
from api.models import User
from api.schemas import UserCreate


async def get_user_by_email(session: AsyncSession, email: str) -> User | None:
    result = await session.execute(select(User).where(User.email == email.lower()))
    return result.scalar_one_or_none()


async def create_user(session: AsyncSession, data: UserCreate) -> User:
    """Create a new user, rejecting duplicate email/phone."""
    duplicate_email = await get_user_by_email(session, data.email)
    if duplicate_email is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered.",
        )

    if data.phone is not None:
        duplicate_phone = await session.execute(select(User).where(User.phone == data.phone))
        if duplicate_phone.scalar_one_or_none() is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Phone number already registered.",
            )

    user = User(
        email=data.email.lower(),
        phone=data.phone,
        full_name=data.full_name,
        password_hash=hash_password(data.password),
        role=data.role,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def authenticate_user(session: AsyncSession, email: str, password: str) -> User | None:
    """Return the user if credentials are valid, else None."""
    user = await get_user_by_email(session, email)
    if user is None:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user


async def get_user(session: AsyncSession, user_id: uuid.UUID) -> User | None:
    result = await session.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()
