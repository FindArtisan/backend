from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from api.models import Role


class UserCreate(BaseModel):
    email: EmailStr
    # bcrypt operates on at most 72 bytes
    password: str = Field(min_length=8, max_length=72)
    full_name: str = Field(min_length=1, max_length=120)
    phone: str | None = Field(default=None, max_length=20)
    role: Role = Role.CLIENT


class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: str
    phone: str | None
    full_name: str
    role: Role
    is_active: bool
