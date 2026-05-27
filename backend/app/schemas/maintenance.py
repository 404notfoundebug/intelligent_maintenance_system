from datetime import datetime
from typing import Any

from pydantic import BaseModel


class MaintenanceRecordItem(BaseModel):
    id: int
    record_no: str
    order_id: int
    device_id: int
    device_name: str
    device_code: str
    device_type: str
    maintenance_company: str | None = None
    responsible_person: str | None = None
    inspection_type: str
    order_no: str
    start_time: datetime | None = None
    end_time: datetime | None = None
    total_items: int
    normal_items: int
    abnormal_items: int
    not_applicable_items: int
    conclusion: str
    report_content: str | None = None
    generated_by: int
    created_at: datetime
    updated_at: datetime


class MaintenanceRecordListData(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[MaintenanceRecordItem]


class MaintenanceReportData(BaseModel):
    record_id: int
    record_no: str
    report_content: str


class MaintenanceResponse(BaseModel):
    code: int = 200
    message: str = "success"
    data: Any
