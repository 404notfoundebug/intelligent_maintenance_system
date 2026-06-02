from datetime import datetime

from sqlalchemy import distinct, func, or_, select
from sqlalchemy.orm import Session

from app.models.case import RepairCase
from app.models.device import Device
from app.models.fault import FaultReport
from app.models.inspection import InspectionOrder
from app.models.knowledge import KnowledgeChunk, KnowledgeFile
from app.models.maintenance import MaintenanceRecord
from app.models.user import User


DEVICE_STATUSES = ["normal", "maintenance", "fault", "disabled"]
FAULT_STATUSES = ["pending", "analyzing", "advised", "processing", "resolved", "closed"]
ORDER_STATUSES = ["pending", "in_progress", "completed", "cancelled"]
CASE_STATUSES = ["pending", "approved", "rejected", "draft"]


class DashboardService:
    @staticmethod
    def _role_name(user: User) -> str | None:
        return user.role.name if user.role else None

    @staticmethod
    def _is_worker(user: User) -> bool:
        return DashboardService._role_name(user) == "worker"

    @staticmethod
    def _worker_device_filter(user: User):
        fault_device_ids = select(FaultReport.device_id).where(
            FaultReport.submitted_by == user.id,
            FaultReport.device_id.is_not(None),
        )
        order_device_ids = select(InspectionOrder.device_id).where(InspectionOrder.assigned_to == user.id)
        return or_(Device.id.in_(fault_device_ids), Device.id.in_(order_device_ids))

    @staticmethod
    def _count(db: Session, model, conditions: list | None = None) -> int:
        stmt = select(func.count()).select_from(model)
        if conditions:
            stmt = stmt.where(*conditions)
        return db.scalar(stmt) or 0

    @staticmethod
    def _status_counts(
        db: Session,
        model,
        status_column,
        statuses: list[str],
        conditions: list | None = None,
    ) -> list[dict]:
        stmt = select(status_column, func.count()).select_from(model)
        if conditions:
            stmt = stmt.where(*conditions)
        stmt = stmt.group_by(status_column)
        raw_counts = {status: count for status, count in db.execute(stmt).all()}
        return [{"status": status, "count": int(raw_counts.get(status, 0))} for status in statuses]

    @staticmethod
    def _fault_conditions(user: User) -> list:
        if DashboardService._is_worker(user):
            return [FaultReport.submitted_by == user.id]
        return []

    @staticmethod
    def _order_conditions(user: User) -> list:
        if DashboardService._is_worker(user):
            return [InspectionOrder.assigned_to == user.id]
        return []

    @staticmethod
    def _case_conditions(user: User) -> list:
        if DashboardService._is_worker(user):
            return [RepairCase.submitted_by == user.id]
        return []

    @staticmethod
    def _maintenance_conditions(user: User) -> list:
        if DashboardService._is_worker(user):
            return [InspectionOrder.assigned_to == user.id]
        return []

    @staticmethod
    def _device_conditions(user: User) -> list:
        if DashboardService._is_worker(user):
            return [DashboardService._worker_device_filter(user)]
        return []

    @staticmethod
    def get_summary(db: Session, current_user: User) -> dict:
        device_conditions = DashboardService._device_conditions(current_user)
        fault_conditions = DashboardService._fault_conditions(current_user)
        order_conditions = DashboardService._order_conditions(current_user)
        case_conditions = DashboardService._case_conditions(current_user)

        maintenance_count_stmt = select(func.count()).select_from(MaintenanceRecord)
        if DashboardService._is_worker(current_user):
            maintenance_count_stmt = maintenance_count_stmt.join(
                InspectionOrder,
                MaintenanceRecord.order_id == InspectionOrder.id,
            ).where(InspectionOrder.assigned_to == current_user.id)

        return {
            "device_count": DashboardService._count(db, Device, device_conditions),
            "normal_device_count": DashboardService._count(db, Device, device_conditions + [Device.status == "normal"]),
            "fault_device_count": DashboardService._count(db, Device, device_conditions + [Device.status == "fault"]),
            "maintenance_device_count": DashboardService._count(
                db,
                Device,
                device_conditions + [Device.status == "maintenance"],
            ),
            "fault_report_count": DashboardService._count(db, FaultReport, fault_conditions),
            "pending_fault_count": DashboardService._count(db, FaultReport, fault_conditions + [FaultReport.status == "pending"]),
            "resolved_fault_count": DashboardService._count(db, FaultReport, fault_conditions + [FaultReport.status == "resolved"]),
            "inspection_order_count": DashboardService._count(db, InspectionOrder, order_conditions),
            "pending_order_count": DashboardService._count(db, InspectionOrder, order_conditions + [InspectionOrder.status == "pending"]),
            "in_progress_order_count": DashboardService._count(
                db,
                InspectionOrder,
                order_conditions + [InspectionOrder.status == "in_progress"],
            ),
            "completed_order_count": DashboardService._count(
                db,
                InspectionOrder,
                order_conditions + [InspectionOrder.status == "completed"],
            ),
            "maintenance_record_count": db.scalar(maintenance_count_stmt) or 0,
            "knowledge_file_count": DashboardService._count(db, KnowledgeFile),
            "knowledge_chunk_count": DashboardService._count(db, KnowledgeChunk),
            "repair_case_count": DashboardService._count(db, RepairCase, case_conditions),
            "pending_case_count": DashboardService._count(db, RepairCase, case_conditions + [RepairCase.status == "pending"]),
            "approved_case_count": DashboardService._count(db, RepairCase, case_conditions + [RepairCase.status == "approved"]),
            "rejected_case_count": DashboardService._count(db, RepairCase, case_conditions + [RepairCase.status == "rejected"]),
        }

    @staticmethod
    def get_device_status(db: Session, current_user: User) -> list[dict]:
        return DashboardService._status_counts(
            db,
            Device,
            Device.status,
            DEVICE_STATUSES,
            DashboardService._device_conditions(current_user),
        )

    @staticmethod
    def get_fault_status(db: Session, current_user: User) -> list[dict]:
        return DashboardService._status_counts(
            db,
            FaultReport,
            FaultReport.status,
            FAULT_STATUSES,
            DashboardService._fault_conditions(current_user),
        )

    @staticmethod
    def get_order_status(db: Session, current_user: User) -> list[dict]:
        return DashboardService._status_counts(
            db,
            InspectionOrder,
            InspectionOrder.status,
            ORDER_STATUSES,
            DashboardService._order_conditions(current_user),
        )

    @staticmethod
    def get_case_status(db: Session, current_user: User) -> list[dict]:
        return DashboardService._status_counts(
            db,
            RepairCase,
            RepairCase.status,
            CASE_STATUSES,
            DashboardService._case_conditions(current_user),
        )

    @staticmethod
    def get_recent_faults(db: Session, current_user: User, limit: int = 5) -> list[dict]:
        stmt = select(FaultReport).order_by(FaultReport.created_at.desc()).limit(limit)
        conditions = DashboardService._fault_conditions(current_user)
        if conditions:
            stmt = stmt.where(*conditions)
        items = db.scalars(stmt).all()
        return [
            {
                "id": item.id,
                "report_no": item.report_no,
                "device_id": item.device_id,
                "device_name": item.device_name,
                "fault_description": item.fault_description,
                "fault_code": item.fault_code,
                "status": item.status,
                "submitted_by": item.submitted_by,
                "created_at": item.created_at,
            }
            for item in items
        ]

    @staticmethod
    def get_recent_orders(db: Session, current_user: User, limit: int = 5) -> list[dict]:
        stmt = select(InspectionOrder).order_by(InspectionOrder.created_at.desc()).limit(limit)
        conditions = DashboardService._order_conditions(current_user)
        if conditions:
            stmt = stmt.where(*conditions)
        items = db.scalars(stmt).all()
        return [
            {
                "id": item.id,
                "order_no": item.order_no,
                "device_id": item.device_id,
                "order_name": item.order_name,
                "inspection_type": item.inspection_type,
                "status": item.status,
                "assigned_to": item.assigned_to,
                "created_by": item.created_by,
                "created_at": item.created_at,
            }
            for item in items
        ]

    @staticmethod
    def get_recent_maintenance_records(db: Session, current_user: User, limit: int = 5) -> list[dict]:
        stmt = select(MaintenanceRecord).order_by(MaintenanceRecord.created_at.desc()).limit(limit)
        if DashboardService._is_worker(current_user):
            stmt = stmt.join(InspectionOrder, MaintenanceRecord.order_id == InspectionOrder.id).where(
                InspectionOrder.assigned_to == current_user.id
            )
        items = db.scalars(stmt).all()
        return [
            {
                "id": item.id,
                "record_no": item.record_no,
                "order_id": item.order_id,
                "device_id": item.device_id,
                "device_name": item.device_name,
                "device_code": item.device_code,
                "inspection_type": item.inspection_type,
                "conclusion": item.conclusion,
                "generated_by": item.generated_by,
                "created_at": item.created_at,
            }
            for item in items
        ]

    @staticmethod
    def _last_month_keys(month_count: int = 6) -> list[str]:
        now = datetime.utcnow()
        year = now.year
        month = now.month
        keys = []
        for offset in range(month_count - 1, -1, -1):
            target_month = month - offset
            target_year = year
            while target_month <= 0:
                target_month += 12
                target_year -= 1
            keys.append(f"{target_year}-{target_month:02d}")
        return keys

    @staticmethod
    def _month_bounds(month_key: str) -> tuple[datetime, datetime]:
        year, month = [int(part) for part in month_key.split("-")]
        start = datetime(year, month, 1)
        if month == 12:
            end = datetime(year + 1, 1, 1)
        else:
            end = datetime(year, month + 1, 1)
        return start, end

    @staticmethod
    def get_monthly_trend(db: Session, current_user: User, month_count: int = 6) -> list[dict]:
        trend = []
        for month_key in DashboardService._last_month_keys(month_count):
            start, end = DashboardService._month_bounds(month_key)
            fault_conditions = DashboardService._fault_conditions(current_user) + [
                FaultReport.created_at >= start,
                FaultReport.created_at < end,
            ]
            order_conditions = DashboardService._order_conditions(current_user) + [
                InspectionOrder.status == "completed",
                InspectionOrder.created_at >= start,
                InspectionOrder.created_at < end,
            ]

            maintenance_stmt = select(func.count()).select_from(MaintenanceRecord).where(
                MaintenanceRecord.created_at >= start,
                MaintenanceRecord.created_at < end,
            )
            if DashboardService._is_worker(current_user):
                maintenance_stmt = maintenance_stmt.join(
                    InspectionOrder,
                    MaintenanceRecord.order_id == InspectionOrder.id,
                ).where(InspectionOrder.assigned_to == current_user.id)

            trend.append(
                {
                    "month": month_key,
                    "fault_count": DashboardService._count(db, FaultReport, fault_conditions),
                    "completed_order_count": DashboardService._count(db, InspectionOrder, order_conditions),
                    "maintenance_record_count": db.scalar(maintenance_stmt) or 0,
                }
            )
        return trend
