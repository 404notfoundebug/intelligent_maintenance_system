from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, field_validator


CASE_STATUSES = {"draft", "pending", "approved", "rejected"}
AUDIT_ACTIONS = {"approve", "reject", "return"}


def normalize_optional_text(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, str):
        value = " ".join(value.strip().split())
        return value or None
    return value


class RepairCaseCreate(BaseModel):
    device_id: int | None = Field(default=None, ge=1)
    fault_report_id: int | None = Field(default=None, ge=1)
    maintenance_record_id: int | None = Field(default=None, ge=1)
    title: str = Field(..., max_length=200)
    device_name: str | None = Field(default=None, max_length=100)
    device_type: str | None = Field(default=None, max_length=50)
    fault_description: str
    fault_reason: str
    repair_process: str
    repair_result: str
    tools_used: str | None = None
    safety_notes: str | None = None

    @field_validator(
        "title",
        "device_name",
        "device_type",
        "fault_description",
        "fault_reason",
        "repair_process",
        "repair_result",
        "tools_used",
        "safety_notes",
        mode="before",
    )
    @classmethod
    def normalize_text(cls, value: Any) -> Any:
        return normalize_optional_text(value)

    @field_validator("title", "fault_description", "fault_reason", "repair_process", "repair_result")
    @classmethod
    def validate_required_text(cls, value: str | None) -> str:
        if not value:
            raise ValueError("参数不能为空")
        return value


class RepairCaseUpdate(BaseModel):
    device_id: int | None = Field(default=None, ge=1)
    fault_report_id: int | None = Field(default=None, ge=1)
    maintenance_record_id: int | None = Field(default=None, ge=1)
    title: str | None = Field(default=None, max_length=200)
    device_name: str | None = Field(default=None, max_length=100)
    device_type: str | None = Field(default=None, max_length=50)
    fault_description: str | None = None
    fault_reason: str | None = None
    repair_process: str | None = None
    repair_result: str | None = None
    tools_used: str | None = None
    safety_notes: str | None = None

    @field_validator(
        "title",
        "device_name",
        "device_type",
        "fault_description",
        "fault_reason",
        "repair_process",
        "repair_result",
        "tools_used",
        "safety_notes",
        mode="before",
    )
    @classmethod
    def normalize_text(cls, value: Any) -> Any:
        return normalize_optional_text(value)

    @field_validator("title", "fault_description", "fault_reason", "repair_process", "repair_result")
    @classmethod
    def validate_non_empty_text(cls, value: str | None) -> str | None:
        if value is None:
            raise ValueError("参数不能为空")
        return value


class RepairCaseAudit(BaseModel):
    action: str = Field(..., max_length=20)
    comment: str | None = None

    @field_validator("action", mode="before")
    @classmethod
    def normalize_action(cls, value: Any) -> Any:
        value = normalize_optional_text(value)
        if value is None:
            raise ValueError("审核动作不能为空")
        return value

    @field_validator("action")
    @classmethod
    def validate_action(cls, value: str) -> str:
        if value not in AUDIT_ACTIONS:
            raise ValueError("不支持的审核动作")
        return value

    @field_validator("comment", mode="before")
    @classmethod
    def normalize_comment(cls, value: Any) -> Any:
        return normalize_optional_text(value)


class CaseAuditRecordResponse(BaseModel):
    id: int
    case_id: int
    action: str
    comment: str | None = None
    operator_id: int
    created_at: datetime
    updated_at: datetime


class RepairCaseResponse(BaseModel):
    id: int
    case_no: str
    device_id: int | None = None
    fault_report_id: int | None = None
    maintenance_record_id: int | None = None
    title: str
    device_name: str | None = None
    device_type: str | None = None
    fault_description: str
    fault_reason: str
    repair_process: str
    repair_result: str
    tools_used: str | None = None
    safety_notes: str | None = None
    status: str
    submitted_by: int
    reviewed_by: int | None = None
    reviewed_at: datetime | None = None
    review_comment: str | None = None
    knowledge_chunk_id: int | None = None
    created_at: datetime
    updated_at: datetime
    audit_records: list[CaseAuditRecordResponse] | None = None


class RepairCaseListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[RepairCaseResponse]


class CaseApiResponse(BaseModel):
    code: int = 200
    message: str = "success"
    data: Any
