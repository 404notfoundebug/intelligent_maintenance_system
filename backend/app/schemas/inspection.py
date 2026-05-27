from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, field_validator


DEVICE_TYPES = {
    "traction_elevator",
    "hydraulic_elevator",
    "escalator",
    "moving_walkway",
}

INSPECTION_TYPES = {"daily", "monthly", "quarterly", "annual", "fault"}
ORDER_STATUSES = {"pending", "in_progress", "completed", "cancelled"}
STEP_RESULTS = {"unchecked", "normal", "abnormal", "not_applicable"}


def normalize_optional_text(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, str):
        value = " ".join(value.strip().split())
        return value or None
    return value


class InspectionTemplateStepCreate(BaseModel):
    step_order: int = Field(..., ge=1)
    area: str = Field(..., max_length=100)
    item_name: str = Field(..., max_length=100)
    item_content: str
    standard: str | None = None
    required_photo: bool = False
    required_remark: bool = False

    @field_validator("area", "item_name", "item_content", mode="before")
    @classmethod
    def normalize_required_text(cls, value: Any) -> Any:
        value = normalize_optional_text(value)
        if value is None:
            raise ValueError("参数不能为空")
        return value

    @field_validator("standard", mode="before")
    @classmethod
    def normalize_standard(cls, value: Any) -> Any:
        return normalize_optional_text(value)


class InspectionTemplateCreate(BaseModel):
    template_name: str = Field(..., max_length=100)
    device_type: str = Field(..., max_length=50)
    inspection_type: str = Field(..., max_length=20)
    description: str | None = None
    is_active: bool = True
    steps: list[InspectionTemplateStepCreate] = Field(default_factory=list)

    @field_validator("template_name", "device_type", "inspection_type", mode="before")
    @classmethod
    def normalize_required_text(cls, value: Any) -> Any:
        value = normalize_optional_text(value)
        if value is None:
            raise ValueError("参数不能为空")
        return value

    @field_validator("description", mode="before")
    @classmethod
    def normalize_description(cls, value: Any) -> Any:
        return normalize_optional_text(value)

    @field_validator("device_type")
    @classmethod
    def validate_device_type(cls, value: str) -> str:
        if value not in DEVICE_TYPES:
            raise ValueError("不支持的设备类型")
        return value

    @field_validator("inspection_type")
    @classmethod
    def validate_inspection_type(cls, value: str) -> str:
        if value not in INSPECTION_TYPES:
            raise ValueError("不支持的点检类型")
        return value


class InspectionTemplateUpdate(BaseModel):
    template_name: str | None = Field(default=None, max_length=100)
    device_type: str | None = Field(default=None, max_length=50)
    inspection_type: str | None = Field(default=None, max_length=20)
    description: str | None = None
    is_active: bool | None = None

    @field_validator("template_name", "device_type", "inspection_type", "description", mode="before")
    @classmethod
    def normalize_text(cls, value: Any) -> Any:
        return normalize_optional_text(value)

    @field_validator("template_name", "device_type", "inspection_type")
    @classmethod
    def validate_non_empty(cls, value: str | None) -> str | None:
        if value is None:
            raise ValueError("参数不能为空")
        return value

    @field_validator("device_type")
    @classmethod
    def validate_device_type(cls, value: str | None) -> str | None:
        if value is not None and value not in DEVICE_TYPES:
            raise ValueError("不支持的设备类型")
        return value

    @field_validator("inspection_type")
    @classmethod
    def validate_inspection_type(cls, value: str | None) -> str | None:
        if value is not None and value not in INSPECTION_TYPES:
            raise ValueError("不支持的点检类型")
        return value


class InspectionTemplateStepItem(BaseModel):
    id: int
    template_id: int
    step_order: int
    area: str
    item_name: str
    item_content: str
    standard: str | None = None
    required_photo: bool
    required_remark: bool
    created_at: datetime
    updated_at: datetime


class InspectionTemplateItem(BaseModel):
    id: int
    template_name: str
    device_type: str
    inspection_type: str
    description: str | None = None
    is_active: bool
    created_by: int
    created_at: datetime
    updated_at: datetime
    steps: list[InspectionTemplateStepItem] | None = None


class InspectionOrderCreate(BaseModel):
    device_id: int = Field(..., ge=1)
    template_id: int = Field(..., ge=1)
    order_name: str = Field(..., max_length=150)
    assigned_to: int | None = Field(default=None, ge=1)
    remark: str | None = None

    @field_validator("order_name", mode="before")
    @classmethod
    def normalize_order_name(cls, value: Any) -> Any:
        value = normalize_optional_text(value)
        if value is None:
            raise ValueError("参数不能为空")
        return value

    @field_validator("remark", mode="before")
    @classmethod
    def normalize_remark(cls, value: Any) -> Any:
        return normalize_optional_text(value)


class InspectionOrderStepUpdate(BaseModel):
    result: str = Field(..., max_length=20)
    remark: str | None = None
    photo_path: str | None = Field(default=None, max_length=500)

    @field_validator("result", mode="before")
    @classmethod
    def normalize_result(cls, value: Any) -> Any:
        value = normalize_optional_text(value)
        if value is None:
            raise ValueError("参数不能为空")
        return value

    @field_validator("result")
    @classmethod
    def validate_result(cls, value: str) -> str:
        if value not in STEP_RESULTS:
            raise ValueError("不支持的检查结果")
        return value

    @field_validator("remark", "photo_path", mode="before")
    @classmethod
    def normalize_optional_fields(cls, value: Any) -> Any:
        return normalize_optional_text(value)


class InspectionOrderStepItem(BaseModel):
    id: int
    order_id: int
    template_step_id: int | None = None
    step_order: int
    area: str
    item_name: str
    item_content: str
    standard: str | None = None
    result: str
    remark: str | None = None
    photo_path: str | None = None
    checked_by: int | None = None
    checked_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class InspectionOrderItem(BaseModel):
    id: int
    order_no: str
    device_id: int
    template_id: int
    order_name: str
    inspection_type: str
    status: str
    assigned_to: int | None = None
    created_by: int
    started_at: datetime | None = None
    completed_at: datetime | None = None
    remark: str | None = None
    created_at: datetime
    updated_at: datetime
    steps: list[InspectionOrderStepItem] | None = None


class InspectionResponse(BaseModel):
    code: int = 200
    message: str = "success"
    data: Any
