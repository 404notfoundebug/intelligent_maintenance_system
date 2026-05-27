from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.api.auth import get_current_active_user, require_roles
from app.core.database import get_db
from app.models.user import User
from app.schemas.device import DeviceCreate, DeviceResponse, DeviceUpdate
from app.services.device_service import DeviceService

router = APIRouter(prefix="/api/devices", tags=["devices"])


def success(data: dict | list | None = None, message: str = "success") -> dict:
    return {"code": 200, "message": message, "data": data or {}}


@router.post("", response_model=DeviceResponse)
def create_device(
    payload: DeviceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["admin", "auditor"])),
):
    try:
        device = DeviceService.create_device(db, payload, current_user.id)
        return success(data=DeviceService.to_dict(device))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"数据库操作失败：{exc}",
        ) from exc


@router.get("", response_model=DeviceResponse)
def list_devices(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    keyword: str | None = None,
    device_type: str | None = None,
    status: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    try:
        total, items = DeviceService.list_devices(
            db=db,
            page=page,
            page_size=page_size,
            keyword=keyword,
            device_type=device_type,
            status=status,
        )
        return success(
            data={
                "total": total,
                "page": page,
                "page_size": page_size,
                "items": [DeviceService.to_dict(item) for item in items],
            }
        )
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"数据库查询失败：{exc}",
        ) from exc


@router.get("/{device_id}", response_model=DeviceResponse)
def get_device(
    device_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    device = DeviceService.get_by_id(db, device_id)
    if device is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="设备不存在")
    return success(data=DeviceService.to_dict(device))


@router.put("/{device_id}", response_model=DeviceResponse)
def update_device(
    device_id: int,
    payload: DeviceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["admin", "auditor"])),
):
    try:
        device = DeviceService.update_device(db, device_id, payload)
        return success(data=DeviceService.to_dict(device))
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"数据库操作失败：{exc}",
        ) from exc


@router.delete("/{device_id}", response_model=DeviceResponse)
def delete_device(
    device_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["admin"])),
):
    try:
        DeviceService.delete_device(db, device_id)
        return success(data={"device_id": device_id}, message="删除成功")
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"数据库操作失败：{exc}",
        ) from exc
