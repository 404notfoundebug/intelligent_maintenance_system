from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.api.auth import get_current_active_user, require_roles
from app.core.database import get_db
from app.models.user import User
from app.schemas.maintenance import MaintenanceResponse
from app.services.maintenance_service import MaintenanceService
from app.services.audit_service import AuditService

router = APIRouter(prefix="/api/maintenance", tags=["maintenance"])


def success(data: dict | list | None = None, message: str = "success") -> dict:
    return {"code": 200, "message": message, "data": data or {}}


def raise_service_error(exc: Exception) -> None:
    if isinstance(exc, PermissionError):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    if isinstance(exc, LookupError):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    if isinstance(exc, ValueError):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    if isinstance(exc, RuntimeError):
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc
    if isinstance(exc, SQLAlchemyError):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"数据库操作失败：{exc}",
        ) from exc
    raise exc


@router.post("/records/from-order/{order_id}", response_model=MaintenanceResponse)
def generate_record_from_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    try:
        record, existed = MaintenanceService.generate_record_from_order(db, order_id, current_user)
        return success(
            data=MaintenanceService.to_dict(record),
            message="该工单已生成维保记录" if existed else "success",
        )
    except Exception as exc:
        raise_service_error(exc)


@router.get("/records", response_model=MaintenanceResponse)
def list_records(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    keyword: str | None = None,
    device_id: int | None = Query(default=None, ge=1),
    inspection_type: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    try:
        total, items = MaintenanceService.list_records(
            db=db,
            page=page,
            page_size=page_size,
            current_user=current_user,
            keyword=keyword,
            device_id=device_id,
            inspection_type=inspection_type,
        )
        return success(
            data={
                "total": total,
                "page": page,
                "page_size": page_size,
                "items": [MaintenanceService.to_dict(item, include_report=False) for item in items],
            }
        )
    except Exception as exc:
        raise_service_error(exc)


@router.get("/records/{record_id}", response_model=MaintenanceResponse)
def get_record(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    try:
        record = MaintenanceService.get_record(db, record_id, current_user)
        if record is None:
            raise LookupError("维保记录不存在")
        return success(data=MaintenanceService.to_dict(record))
    except Exception as exc:
        raise_service_error(exc)


@router.get("/records/{record_id}/report", response_model=MaintenanceResponse)
def get_report(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    try:
        return success(data=MaintenanceService.get_report(db, record_id, current_user))
    except Exception as exc:
        raise_service_error(exc)


@router.delete("/records/{record_id}", response_model=MaintenanceResponse)
def delete_record(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["admin"])),
):
    try:
        MaintenanceService.delete_record(db, record_id)
        return success(data={"record_id": record_id}, message="删除成功")
    except Exception as exc:
        raise_service_error(exc)


class AuditRequest(BaseModel):
    status: str
    reject_reason: str | None = None


@router.put("/records/{record_id}/audit", response_model=MaintenanceResponse)
def audit_record(
    record_id: int,
    payload: AuditRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["admin"])),
):
    try:
        record = MaintenanceService.audit_record(
            db, record_id, payload.status, current_user,
            reject_reason=payload.reject_reason,
        )
        AuditService.write(
            db, payload.status, "维保审核", "maintenance_record",
            target_id=record.id, target_name=record.record_no,
            detail=f"维保记录审核{payload.status}" + (f"，驳回原因：{payload.reject_reason}" if payload.reject_reason else ""),
            operator=current_user,
        )
        return success(data=MaintenanceService.to_dict(record), message="审核完成")
    except Exception as exc:
        raise_service_error(exc)
