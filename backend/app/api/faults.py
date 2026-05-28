from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.api.auth import get_current_active_user, require_roles
from app.core.database import get_db
from app.models.user import User
from app.schemas.fault import FaultApiResponse, FaultReportCreate, FaultReportUpdateStatus
from app.services.fault_service import FaultService

router = APIRouter(prefix="/api/faults", tags=["faults"])


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
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
    if isinstance(exc, SQLAlchemyError):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"数据库操作失败：{exc}",
        ) from exc
    raise exc


@router.post("", response_model=FaultApiResponse)
def create_fault_report(
    payload: FaultReportCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    try:
        fault_report = FaultService.create_fault_report(db, payload, current_user)
        return success(data=FaultService.report_to_dict(fault_report))
    except Exception as exc:
        raise_service_error(exc)


@router.post("/{fault_id}/images", response_model=FaultApiResponse)
def upload_fault_image(
    fault_id: int,
    file: UploadFile = File(...),
    image_type: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    try:
        image = FaultService.upload_fault_image(
            db=db,
            fault_id=fault_id,
            file=file,
            image_type=image_type,
            current_user=current_user,
        )
        return success(
            data={
                "image_id": image.id,
                "fault_report_id": image.fault_report_id,
                "original_filename": image.original_filename,
                "image_type": image.image_type,
                "vision_status": image.vision_status,
            }
        )
    except Exception as exc:
        raise_service_error(exc)


@router.get("", response_model=FaultApiResponse)
def list_fault_reports(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    keyword: str | None = None,
    device_id: int | None = Query(default=None, ge=1),
    status: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    try:
        total, items = FaultService.list_fault_reports(
            db=db,
            page=page,
            page_size=page_size,
            current_user=current_user,
            keyword=keyword,
            device_id=device_id,
            status=status,
        )
        return success(
            data={
                "total": total,
                "page": page,
                "page_size": page_size,
                "items": [FaultService.report_to_dict(item) for item in items],
            }
        )
    except Exception as exc:
        raise_service_error(exc)


@router.get("/{fault_id}", response_model=FaultApiResponse)
def get_fault_report(
    fault_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    try:
        fault_report = FaultService.get_fault_report(db, fault_id, current_user)
        if fault_report is None:
            raise LookupError("故障记录不存在")
        return success(data=FaultService.report_to_dict(fault_report, include_images=True))
    except Exception as exc:
        raise_service_error(exc)


@router.put("/{fault_id}/status", response_model=FaultApiResponse)
def update_fault_status(
    fault_id: int,
    payload: FaultReportUpdateStatus,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    try:
        fault_report = FaultService.update_fault_status(db, fault_id, payload, current_user)
        return success(data=FaultService.report_to_dict(fault_report, include_images=True))
    except Exception as exc:
        raise_service_error(exc)


@router.post("/{fault_id}/images/{image_id}/analyze", response_model=FaultApiResponse)
def analyze_fault_image(
    fault_id: int,
    image_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    try:
        image = FaultService.analyze_fault_image(db, fault_id, image_id, current_user)
        return success(
            data={
                "image_id": image.id,
                "vision_status": image.vision_status,
                "vision_result": image.vision_result,
            }
        )
    except Exception as exc:
        raise_service_error(exc)


@router.post("/{fault_id}/repair-advice", response_model=FaultApiResponse)
def generate_repair_advice_from_fault(
    fault_id: int,
    top_k: int = Query(default=5, ge=1, le=20),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    try:
        fault_report, qa_record, references = FaultService.generate_repair_advice_from_fault(
            db=db,
            fault_id=fault_id,
            current_user=current_user,
            top_k=top_k,
        )
        return success(
            data={
                "fault_report_id": fault_report.id,
                "qa_record_id": qa_record.id,
                "answer": qa_record.answer,
                "references": references,
            }
        )
    except Exception as exc:
        raise_service_error(exc)


@router.delete("/{fault_id}", response_model=FaultApiResponse)
def delete_fault_report(
    fault_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["admin"])),
):
    try:
        FaultService.delete_fault_report(db, fault_id)
        return success(data={"fault_id": fault_id}, message="删除成功")
    except Exception as exc:
        raise_service_error(exc)
