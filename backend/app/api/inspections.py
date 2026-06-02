from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.api.auth import get_current_active_user, require_roles
from app.core.database import get_db
from app.models.user import User
from app.schemas.inspection import (
    InspectionOrderCreate,
    InspectionOrderStepUpdate,
    InspectionResponse,
    InspectionTemplateCreate,
    InspectionTemplateUpdate,
)
from app.services.inspection_service import InspectionService

router = APIRouter(prefix="/api/inspections", tags=["inspections"])


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


@router.post("/templates", response_model=InspectionResponse)
def create_template(
    payload: InspectionTemplateCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["admin", "auditor"])),
):
    try:
        template = InspectionService.create_template(db, payload, current_user.id)
        return success(data=InspectionService.template_to_dict(template, include_steps=True))
    except Exception as exc:
        raise_service_error(exc)


@router.get("/templates", response_model=InspectionResponse)
def list_templates(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    device_type: str | None = None,
    inspection_type: str | None = None,
    is_active: bool | None = None,
    keyword: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    try:
        total, items = InspectionService.list_templates(
            db=db,
            page=page,
            page_size=page_size,
            device_type=device_type,
            inspection_type=inspection_type,
            is_active=is_active,
            keyword=keyword,
        )
        return success(
            data={
                "total": total,
                "page": page,
                "page_size": page_size,
                "items": [InspectionService.template_to_dict(item) for item in items],
            }
        )
    except Exception as exc:
        raise_service_error(exc)


@router.get("/templates/{template_id}", response_model=InspectionResponse)
def get_template(
    template_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    template = InspectionService.get_template(db, template_id)
    if template is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="点检模板不存在")
    return success(data=InspectionService.template_to_dict(template, include_steps=True))


@router.put("/templates/{template_id}", response_model=InspectionResponse)
def update_template(
    template_id: int,
    payload: InspectionTemplateUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["admin", "auditor"])),
):
    try:
        template = InspectionService.update_template(db, template_id, payload)
        return success(data=InspectionService.template_to_dict(template, include_steps=True))
    except Exception as exc:
        raise_service_error(exc)


@router.delete("/templates/{template_id}", response_model=InspectionResponse)
def delete_template(
    template_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["admin"])),
):
    try:
        template, disabled = InspectionService.delete_or_disable_template(db, template_id)
        if disabled and template is not None:
            return success(
                data=InspectionService.template_to_dict(template, include_steps=True),
                message="模板已有工单使用，已停用",
            )
        return success(data={"template_id": template_id}, message="删除成功")
    except Exception as exc:
        raise_service_error(exc)


@router.post("/orders", response_model=InspectionResponse)
def create_order(
    payload: InspectionOrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    try:
        order = InspectionService.create_order(db, payload, current_user)
        return success(data=InspectionService.order_to_dict(order, include_steps=True))
    except Exception as exc:
        raise_service_error(exc)


@router.get("/orders", response_model=InspectionResponse)
def list_orders(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    device_id: int | None = Query(default=None, ge=1),
    status: str | None = None,
    assigned_to: int | None = Query(default=None, ge=1),
    keyword: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    try:
        total, items = InspectionService.list_orders(
            db=db,
            page=page,
            page_size=page_size,
            current_user=current_user,
            device_id=device_id,
            status=status,
            assigned_to=assigned_to,
            keyword=keyword,
        )
        return success(
            data={
                "total": total,
                "page": page,
                "page_size": page_size,
                "items": [InspectionService.order_to_dict(item) for item in items],
            }
        )
    except Exception as exc:
        raise_service_error(exc)


@router.get("/orders/{order_id}", response_model=InspectionResponse)
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    try:
        order = InspectionService.get_order(db, order_id, current_user)
        if order is None:
            raise LookupError("点检工单不存在")
        return success(data=InspectionService.order_to_dict(order, include_steps=True))
    except Exception as exc:
        raise_service_error(exc)


@router.put("/orders/{order_id}/start", response_model=InspectionResponse)
def start_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    try:
        order = InspectionService.start_order(db, order_id, current_user)
        return success(data=InspectionService.order_to_dict(order, include_steps=True))
    except Exception as exc:
        raise_service_error(exc)


@router.put("/orders/{order_id}/steps/{step_id}", response_model=InspectionResponse)
def update_order_step(
    order_id: int,
    step_id: int,
    payload: InspectionOrderStepUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    try:
        step = InspectionService.update_order_step(db, order_id, step_id, payload, current_user)
        return success(data=InspectionService.order_step_to_dict(step))
    except Exception as exc:
        raise_service_error(exc)


@router.post("/orders/{order_id}/steps/{step_id}/photo", response_model=InspectionResponse)
def upload_order_step_photo(
    order_id: int,
    step_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    try:
        data = InspectionService.upload_step_photo(
            db=db,
            order_id=order_id,
            step_id=step_id,
            file=file,
            current_user=current_user,
        )
        return success(data=data)
    except Exception as exc:
        raise_service_error(exc)


@router.put("/orders/{order_id}/complete", response_model=InspectionResponse)
def complete_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    try:
        order = InspectionService.complete_order(db, order_id, current_user)
        return success(data=InspectionService.order_to_dict(order, include_steps=True))
    except Exception as exc:
        raise_service_error(exc)


@router.delete("/orders/{order_id}", response_model=InspectionResponse)
def delete_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["admin", "auditor"])),
):
    try:
        InspectionService.delete_order(db, order_id)
        return success(data={"order_id": order_id}, message="删除成功")
    except Exception as exc:
        raise_service_error(exc)
