from datetime import datetime
from typing import Any

from pydantic import BaseModel


class KnowledgeUploadData(BaseModel):
    file_id: int
    original_filename: str
    file_type: str
    parse_status: str
    chunk_count: int
    parse_message: str | None = None


class KnowledgeFileItem(BaseModel):
    id: int
    original_filename: str
    stored_filename: str
    file_type: str
    document_type: str
    file_size: int
    parse_status: str
    parse_message: str | None = None
    uploaded_by: int
    created_at: datetime
    updated_at: datetime


class KnowledgeFileListData(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[KnowledgeFileItem]


class KnowledgeFileDetail(KnowledgeFileItem):
    file_path: str
    chunk_count: int


class KnowledgeChunkItem(BaseModel):
    id: int
    file_id: int
    chunk_index: int
    title: str | None = None
    content: str
    metadata_json: dict[str, Any] | None = None
    created_at: datetime
    updated_at: datetime


class KnowledgeChunkListData(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[KnowledgeChunkItem]


class ApiResponse(BaseModel):
    code: int = 200
    message: str = "success"
    data: Any
