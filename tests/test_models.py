import uuid
from decimal import Decimal

import pytest
from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from api.models import ArtisanProfile, Role, TradeCategory, User

pytestmark = pytest.mark.anyio

CONSTRAINT_ERROR = "UNIQUE"


async def _create_artisan(session) -> User:  # noqa: ANN001
    user = User(
        email="akin@example.com",
        phone="+2348012345678",
        full_name="Akin the Plumber",
        password_hash="argon2$hashed",
        role=Role.ARTISAN,
    )
    session.add(user)
    await session.flush()
    session.add(
        ArtisanProfile(
            user_id=user.id,
            trade_category=TradeCategory.PLUMBER,
            bio="Certified plumber with 7 years of experience.",
            years_experience=7,
            hourly_rate=Decimal("2500.00"),
        )
    )
    await session.commit()
    return user


async def test_artisan_profile_linked_to_user(db_session) -> None:
    user = await _create_artisan(db_session)

    loaded = (
        await db_session.execute(
            select(User)
            .where(User.email == "akin@example.com")
            .options(selectinload(User.artisan_profile))
        )
    ).scalar_one()

    assert loaded.id == user.id
    assert loaded.role is Role.ARTISAN
    assert loaded.artisan_profile is not None
    assert loaded.artisan_profile.user_id == loaded.id
    assert loaded.artisan_profile.trade_category is TradeCategory.PLUMBER
    assert loaded.artisan_profile.user is loaded


async def test_artisan_profile_defaults(db_session) -> None:
    user = await _create_artisan(db_session)

    profile = (
        await db_session.execute(select(ArtisanProfile).where(ArtisanProfile.user_id == user.id))
    ).scalar_one()

    assert profile.is_available is True
    assert profile.years_experience == 7
    assert profile.hourly_rate == Decimal("2500.00")
    assert profile.created_at is not None
    assert profile.updated_at is not None


async def test_email_is_unique(db_session) -> None:
    await _create_artisan(db_session)
    duplicate = User(
        email="akin@example.com",
        full_name="Someone else",
        password_hash="x",
    )
    db_session.add(duplicate)

    with pytest.raises(Exception, match=CONSTRAINT_ERROR):
        await db_session.commit()


async def test_cascade_delete_removes_profile(db_session) -> None:
    user = await _create_artisan(db_session)

    count_before = (
        await db_session.execute(select(func.count()).select_from(ArtisanProfile))
    ).scalar_one()
    assert count_before == 1

    await db_session.delete(user)
    await db_session.commit()

    remaining = (
        await db_session.execute(select(func.count()).select_from(ArtisanProfile))
    ).scalar_one()
    assert remaining == 0


async def test_multiple_artisan_profiles_rejected(db_session) -> None:
    """The unique FK on user_id enforces the 1:1 relationship."""
    user = await _create_artisan(db_session)
    db_session.add(
        ArtisanProfile(
            id=uuid.uuid4(),
            user_id=user.id,
            trade_category=TradeCategory.ELECTRICIAN,
        )
    )

    with pytest.raises(Exception, match=CONSTRAINT_ERROR):
        await db_session.commit()
