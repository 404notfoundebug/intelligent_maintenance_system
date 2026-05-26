from datetime import datetime

from pydantic import BaseModel, ConfigDict


class UserBase(BaseModel):
    username: str
    real_name: str | None = None
    phone: str | None = None
    email: str | None = None


class UserResponse(UserBase):
    id: int
    role: str
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CurrentUserResponse(BaseModel):
    id: int
    username: str
    real_name: str | None = None
    role: str

    model_config = ConfigDict(from_attributes=True)
