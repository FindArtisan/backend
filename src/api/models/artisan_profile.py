"""Artisan profile model - role-specific data for artisan accounts.

A 1:1 extension of the ``users`` table: every artisan has exactly one
``User`` row, and artisan-only attributes (trade, experience, pricing)
live here. A future ``client_profiles`` table would follow the same
``user_id`` foreign-key pattern when client-specific data is needed.
"""

import uuid
from decimal import Decimal
from enum import StrEnum
from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy import Enum as SAEnum
from sqlalchemy import ForeignKey, Numeric, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from api.models.user import User


class TradeCategory(StrEnum):
    PLUMBER = "plumber"
    ELECTRICIAN = "electrician"
    CARPENTER = "carpenter"
    MASON = "mason"
    PAINTER = "painter"
    WELDER = "welder"
    TAILOR = "tailor"
    MECHANIC = "mechanic"
    LOCKSMITH = "locksmith"
    CLEANER = "cleaner"


class ArtisanProfile(Base, TimestampMixin):
    __tablename__ = "artisan_profiles"

    id: Mapped[uuid.UUID] = mapped_column(sa.Uuid, primary_key=True, default=uuid.uuid4)
    # 1:1 with users; deleting a user deletes their profile.
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), unique=True, index=True
    )
    user: Mapped["User"] = relationship(back_populates="artisan_profile")

    trade_category: Mapped[TradeCategory] = mapped_column(
        SAEnum(
            TradeCategory,
            native_enum=False,
            length=32,
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
        ),
        index=True,
    )
    bio: Mapped[str | None] = mapped_column(Text)
    years_experience: Mapped[int] = mapped_column(default=0, server_default=sa.text("0"))
    hourly_rate: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    is_available: Mapped[bool] = mapped_column(default=True, server_default=sa.true())

    def __repr__(self) -> str:
        return (
            f"ArtisanProfile(id={self.id!r}, user_id={self.user_id!r}, "
            f"trade_category={self.trade_category!r})"
        )
