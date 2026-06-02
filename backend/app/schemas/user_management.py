from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, field_validator


VALID_ROLES = {"admin", "worker", "auditor"}


def normalize_optional_text(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, str):
        value = " ".join(value.strip().split())
        return value or None
    return value


class UserCreate(BaseModel):
    username: str = Field(..., max_length=64)
    password: str
    real_name: str | None = Field(default=None, max_length=100)
    phone: str | None = Field(default=None, max_length=32)
    email: str | None = Field(default=None, max_length=128)
    role: str
    is_active: bool = True

    @field_validator("username", "password", "real_name", "phone", "email", "role", mode="before")
    @classmethod
    def normalize_text(cls, value: Any) -> Any:
        return normalize_optional_text(value)

    @field_validator("username", "password", "role")
    @classmethod
    def validate_required_text(cls, value: str | None) -> str:
        if not value:
            raise ValueError("参数不能为空")
        return value

    @field_validator("role")
    @classmethod
    def validate_role(cls, value: str) -> str:
        if value not in VALID_ROLES:
            raise ValueError("角色不存在")
        return value


class UserUpdate(BaseModel):
    username: str | None = Field(default=None, max_length=64)
    real_name: str | None = Field(default=None, max_length=100)
    phone: str | None = Field(default=None, max_length=32)
    email: str | None = Field(default=None, max_length=128)

    @field_validator("username", "real_name", "phone", "email", mode="before")
    @classmethod
    def normalize_text(cls, value: Any) -> Any:
        return normalize_optional_text(value)

    @field_validator("username")
    @classmethod
    def validate_username(cls, value: str | None) -> str | None:
        if value is None:
            raise ValueError("参数不能为空")
        return value


class UserRoleUpdate(BaseModel):
    role: str

    @field_validator("role", mode="before")
    @classmethod
    def normalize_role(cls, value: Any) -> Any:
        value = normalize_optional_text(value)
        if value is None:
            raise ValueError("角色不能为空")
        return value

    @field_validator("role")
    @classmethod
    def validate_role(cls, value: str) -> str:
        if value not in VALID_ROLES:
            raise ValueError("角色不存在")
        return value


class UserStatusUpdate(BaseModel):
    is_active: bool


class UserResetPassword(BaseModel):
    new_password: str

    @field_validator("new_password", mode="before")
    @classmethod
    def normalize_password(cls, value: Any) -> Any:
        value = normalize_optional_text(value)
        if value is None:
            raise ValueError("密码不能为空")
        return value


class UserChangePassword(BaseModel):
    old_password: str
    new_password: str

    @field_validator("old_password", "new_password", mode="before")
    @classmethod
    def normalize_password(cls, value: Any) -> Any:
        value = normalize_optional_text(value)
        if value is None:
            raise ValueError("密码不能为空")
        return value


class RoleResponse(BaseModel):
    id: int
    name: str
    description: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class UserResponse(BaseModel):
    id: int
    username: str
    real_name: str | None = None
    phone: str | None = None
    email: str | None = None
    role: str
    is_active: bool
    created_at: datetime
    updated_at: datetime


class UserListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[UserResponse]


class UserApiResponse(BaseModel):
    code: int = 200
    message: str = "success"
    data: Any
