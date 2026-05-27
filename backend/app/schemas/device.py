from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, field_validator


DEVICE_TYPES = {
    "traction_elevator",
    "hydraulic_elevator",
    "escalator",
    "moving_walkway",
}

DEVICE_STATUSES = {"normal", "maintenance", "fault", "disabled"}


class DeviceBase(BaseModel):
    device_name: str | None = Field(default=None, max_length=100)
    device_code: str | None = Field(default=None, max_length=64)
    device_type: str | None = Field(default=None, max_length=50)
    device_model: str | None = Field(default=None, max_length=100)
    manufacturer: str | None = Field(default=None, max_length=100)
    installation_location: str | None = Field(default=None, max_length=200)
    maintenance_company: str | None = Field(default=None, max_length=100)
    responsible_person: str | None = Field(default=None, max_length=50)
    contact_phone: str | None = Field(default=None, max_length=32)
    status: str | None = Field(default="normal", max_length=20)
    remark: str | None = None

    @field_validator(
        "device_name",
        "device_code",
        "device_type",
        "device_model",
        "manufacturer",
        "installation_location",
        "maintenance_company",
        "responsible_person",
        "contact_phone",
        "status",
        mode="before",
    )
    @classmethod
    def normalize_text(cls, value: Any) -> Any:
        if value is None:
            return None
        if isinstance(value, str):
            value = " ".join(value.strip().split())
            return value or None
        return value

    @field_validator("device_type")
    @classmethod
    def validate_device_type(cls, value: str | None) -> str | None:
        if value is not None and value not in DEVICE_TYPES:
            raise ValueError("不支持的设备类型")
        return value

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: str | None) -> str | None:
        if value is not None and value not in DEVICE_STATUSES:
            raise ValueError("不支持的设备状态")
        return value


class DeviceCreate(DeviceBase):
    device_name: str = Field(..., max_length=100)
    device_code: str = Field(..., max_length=64)
    device_type: str = Field(..., max_length=50)
    status: str = Field(default="normal", max_length=20)

    @field_validator("device_name", "device_code", "device_type")
    @classmethod
    def validate_required_text(cls, value: str | None) -> str:
        if not value:
            raise ValueError("参数不能为空")
        return value


class DeviceUpdate(DeviceBase):
    status: str | None = Field(default=None, max_length=20)

    @field_validator("device_name", "device_code", "device_type")
    @classmethod
    def validate_non_empty_required_fields(cls, value: str | None) -> str | None:
        if value is None:
            raise ValueError("参数不能为空")
        return value


class DeviceItem(BaseModel):
    id: int
    device_name: str
    device_code: str
    device_type: str
    device_model: str | None = None
    manufacturer: str | None = None
    installation_location: str | None = None
    maintenance_company: str | None = None
    responsible_person: str | None = None
    contact_phone: str | None = None
    status: str
    remark: str | None = None
    created_by: int
    created_at: datetime
    updated_at: datetime


class DeviceListData(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[DeviceItem]


class DeviceResponse(BaseModel):
    code: int = 200
    message: str = "success"
    data: Any
