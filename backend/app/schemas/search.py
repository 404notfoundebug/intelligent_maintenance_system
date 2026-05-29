from typing import Any

from pydantic import BaseModel, Field, field_validator


class SearchRequest(BaseModel):
    query: str = Field(..., description="故障现象或检索问题")
    top_k: int = Field(default=5, ge=1, le=50, description="返回结果数量")
    document_type: str | None = Field(default=None, description="文档类型过滤")
    file_id: int | None = Field(default=None, ge=1, description="指定文件 ID")

    @field_validator("query")
    @classmethod
    def validate_query(cls, value: str) -> str:
        normalized = " ".join(value.strip().split())
        if not normalized:
            raise ValueError("query 不能为空")
        return normalized

    @field_validator("document_type")
    @classmethod
    def normalize_document_type(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        return value or None


class SearchResultItem(BaseModel):
    chunk_id: int
    file_id: int | None = None
    source_file_name: str
    document_type: str
    chunk_index: int
    title: str | None = None
    content: str
    score: float


class SearchData(BaseModel):
    query: str
    total: int
    results: list[SearchResultItem]


class SearchResponse(BaseModel):
    code: int = 200
    message: str = "success"
    data: Any
