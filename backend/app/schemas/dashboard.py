from datetime import datetime
from typing import Any

from pydantic import BaseModel


class DashboardSummaryResponse(BaseModel):
    device_count: int
    normal_device_count: int
    fault_device_count: int
    maintenance_device_count: int
    fault_report_count: int
    pending_fault_count: int
    resolved_fault_count: int
    inspection_order_count: int
    pending_order_count: int
    in_progress_order_count: int
    completed_order_count: int
    maintenance_record_count: int
    knowledge_file_count: int
    knowledge_chunk_count: int
    repair_case_count: int
    pending_case_count: int
    approved_case_count: int
    rejected_case_count: int


class StatusCountItem(BaseModel):
    status: str
    count: int


class MonthlyTrendItem(BaseModel):
    month: str
    fault_count: int
    completed_order_count: int
    maintenance_record_count: int


class RecentFaultItem(BaseModel):
    id: int
    report_no: str
    device_id: int | None = None
    device_name: str | None = None
    fault_description: str
    fault_code: str | None = None
    status: str
    submitted_by: int
    created_at: datetime


class RecentOrderItem(BaseModel):
    id: int
    order_no: str
    device_id: int
    order_name: str
    inspection_type: str
    status: str
    assigned_to: int | None = None
    created_by: int
    created_at: datetime


class RecentMaintenanceRecordItem(BaseModel):
    id: int
    record_no: str
    order_id: int
    device_id: int
    device_name: str
    device_code: str
    inspection_type: str
    conclusion: str
    generated_by: int
    created_at: datetime


class DashboardResponse(BaseModel):
    code: int = 200
    message: str = "success"
    data: Any
