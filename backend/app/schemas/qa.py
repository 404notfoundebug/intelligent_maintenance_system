from typing import Any

from pydantic import BaseModel, Field, field_validator


class RepairAdviceRequest(BaseModel):
    device_name: str | None = Field(default=None, description="设备名称")
    device_model: str | None = Field(default=None, description="设备型号")
    fault_description: str = Field(..., description="故障现象")
    top_k: int = Field(default=5, ge=1, le=20, description="检索知识片段数量")

    @field_validator("device_name", "device_model")
    @classmethod
    def normalize_optional_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = " ".join(value.strip().split())
        return value or None

    @field_validator("fault_description")
    @classmethod
    def validate_fault_description(cls, value: str) -> str:
        normalized = " ".join(value.strip().split())
        if not normalized:
            raise ValueError("fault_description 不能为空")
        return normalized


class RepairAdviceReference(BaseModel):
    chunk_id: int
    file_id: int
    source_file_name: str
    document_type: str
    chunk_index: int
    score: float


class RepairAdviceData(BaseModel):
    record_id: int
    answer: str
    references: list[RepairAdviceReference]


class RepairAdviceResponse(BaseModel):
    code: int = 200
    message: str = "success"
    data: Any
