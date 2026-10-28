"""User model - a single accounts table for all users.

FindArtisan users are either clients (people requesting artisan services)
or artisans (people offering services). Auth- and identity-related data
lives here; role-specific attributes live in profile tables linked by
``user_id`` (see ``api.models.artisan_profile``).
"""

import uuid
from enum import StrEnum
from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy import Enum as SAEnum
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from api.models.artisan_profile import ArtisanProfile


class Role(StrEnum):
    CLIENT = "client"
    ARTISAN = "artisan"


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(sa.Uuid, primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    phone: Mapped[str | None] = mapped_column(String(20), unique=True)
    full_name: Mapped[str] = mapped_column(String(120))
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[Role] = mapped_column(
        SAEnum(
            Role,
            native_enum=False,
            length=16,
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
        ),
        default=Role.CLIENT,
        server_default=Role.CLIENT.value,
    )
    is_active: Mapped[bool] = mapped_column(default=True, server_default=sa.true())

    artisan_profile: Mapped["ArtisanProfile | None"] = relationship(
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, email={self.email!r}, role={self.role!r})"
