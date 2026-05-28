from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, field_validator


FAULT_STATUSES = {"pending", "analyzing", "advised", "processing", "resolved", "closed"}
IMAGE_TYPES = {"fault_code", "control_cabinet", "door_system", "escalator_part", "other"}


def normalize_optional_text(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, str):
        value = " ".join(value.strip().split())
        return value or None
    return value


class FaultReportCreate(BaseModel):
    device_id: int | None = Field(default=None, ge=1)
    device_name: str | None = Field(default=None, max_length=100)
    device_model: str | None = Field(default=None, max_length=100)
    fault_description: str
    fault_code: str | None = Field(default=None, max_length=100)
    location: str | None = Field(default=None, max_length=200)

    @field_validator("device_name", "device_model", "fault_code", "location", mode="before")
    @classmethod
    def normalize_text(cls, value: Any) -> Any:
        return normalize_optional_text(value)

    @field_validator("fault_description", mode="before")
    @classmethod
    def normalize_fault_description(cls, value: Any) -> Any:
        value = normalize_optional_text(value)
        if value is None:
            raise ValueError("故障现象描述不能为空")
        return value


class FaultReportUpdateStatus(BaseModel):
    status: str = Field(..., max_length=20)

    @field_validator("status", mode="before")
    @classmethod
    def normalize_status(cls, value: Any) -> Any:
        value = normalize_optional_text(value)
        if value is None:
            raise ValueError("状态不能为空")
        return value

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: str) -> str:
        if value not in FAULT_STATUSES:
            raise ValueError("不支持的故障处理状态")
        return value


class FaultImageResponse(BaseModel):
    id: int
    fault_report_id: int
    original_filename: str
    stored_filename: str | None = None
    file_path: str | None = None
    file_type: str
    image_type: str
    file_size: int | None = None
    vision_status: str
    vision_result: str | None = None
    vision_error: str | None = None
    uploaded_by: int | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class FaultReportResponse(BaseModel):
    id: int
    report_no: str
    device_id: int | None = None
    device_name: str | None = None
    device_model: str | None = None
    fault_description: str
    fault_code: str | None = None
    location: str | None = None
    status: str
    submitted_by: int
    advice_record_id: int | None = None
    created_at: datetime
    updated_at: datetime
    images: list[FaultImageResponse] | None = None


class FaultReportListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[FaultReportResponse]


class FaultImageAnalyzeResponse(BaseModel):
    image_id: int
    vision_status: str
    vision_result: str | None = None
    vision_error: str | None = None


class FaultRepairAdviceResponse(BaseModel):
    fault_report_id: int
    qa_record_id: int
    answer: str
    references: list[dict]


class FaultApiResponse(BaseModel):
    code: int = 200
    message: str = "success"
    data: Any
