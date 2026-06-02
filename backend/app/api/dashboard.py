from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.api.auth import get_current_active_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.dashboard import DashboardResponse
from app.services.dashboard_service import DashboardService

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


def success(data: dict | list | None = None, message: str = "success") -> dict:
    return {"code": 200, "message": message, "data": data or {}}


def raise_dashboard_error(exc: Exception) -> None:
    if isinstance(exc, SQLAlchemyError):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"数据库统计查询失败：{exc}",
        ) from exc
    raise exc


@router.get("/summary", response_model=DashboardResponse)
def get_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    try:
        return success(data=DashboardService.get_summary(db, current_user))
    except Exception as exc:
        raise_dashboard_error(exc)


@router.get("/device-status", response_model=DashboardResponse)
def get_device_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    try:
        return success(data=DashboardService.get_device_status(db, current_user))
    except Exception as exc:
        raise_dashboard_error(exc)


@router.get("/fault-status", response_model=DashboardResponse)
def get_fault_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    try:
        return success(data=DashboardService.get_fault_status(db, current_user))
    except Exception as exc:
        raise_dashboard_error(exc)


@router.get("/order-status", response_model=DashboardResponse)
def get_order_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    try:
        return success(data=DashboardService.get_order_status(db, current_user))
    except Exception as exc:
        raise_dashboard_error(exc)


@router.get("/case-status", response_model=DashboardResponse)
def get_case_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    try:
        return success(data=DashboardService.get_case_status(db, current_user))
    except Exception as exc:
        raise_dashboard_error(exc)


@router.get("/recent-faults", response_model=DashboardResponse)
def get_recent_faults(
    limit: int = Query(default=5, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    try:
        return success(data=DashboardService.get_recent_faults(db, current_user, limit))
    except Exception as exc:
        raise_dashboard_error(exc)


@router.get("/recent-orders", response_model=DashboardResponse)
def get_recent_orders(
    limit: int = Query(default=5, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    try:
        return success(data=DashboardService.get_recent_orders(db, current_user, limit))
    except Exception as exc:
        raise_dashboard_error(exc)


@router.get("/recent-maintenance-records", response_model=DashboardResponse)
def get_recent_maintenance_records(
    limit: int = Query(default=5, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    try:
        return success(data=DashboardService.get_recent_maintenance_records(db, current_user, limit))
    except Exception as exc:
        raise_dashboard_error(exc)


@router.get("/monthly-trend", response_model=DashboardResponse)
def get_monthly_trend(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    try:
        return success(data=DashboardService.get_monthly_trend(db, current_user))
    except Exception as exc:
        raise_dashboard_error(exc)
