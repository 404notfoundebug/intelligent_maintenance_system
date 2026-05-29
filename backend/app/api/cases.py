from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.api.auth import get_current_active_user, require_roles
from app.core.database import get_db
from app.models.user import User
from app.schemas.case import CaseApiResponse, RepairCaseAudit, RepairCaseCreate, RepairCaseUpdate
from app.services.case_service import CaseService

router = APIRouter(prefix="/api/cases", tags=["cases"])


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


@router.post("", response_model=CaseApiResponse)
def create_case(
    payload: RepairCaseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    try:
        repair_case = CaseService.create_case(db, payload, current_user)
        return success(data=CaseService.case_to_dict(repair_case, include_audit_records=True))
    except Exception as exc:
        raise_service_error(exc)


@router.get("", response_model=CaseApiResponse)
def list_cases(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    keyword: str | None = None,
    status: str | None = None,
    device_id: int | None = Query(default=None, ge=1),
    submitted_by: int | None = Query(default=None, ge=1),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    try:
        total, items = CaseService.list_cases(
            db=db,
            page=page,
            page_size=page_size,
            current_user=current_user,
            keyword=keyword,
            status=status,
            device_id=device_id,
            submitted_by=submitted_by,
        )
        return success(
            data={
                "total": total,
                "page": page,
                "page_size": page_size,
                "items": [CaseService.case_to_dict(item) for item in items],
            }
        )
    except Exception as exc:
        raise_service_error(exc)


@router.get("/{case_id}", response_model=CaseApiResponse)
def get_case(
    case_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    try:
        repair_case = CaseService.get_case(db, case_id, current_user)
        if repair_case is None:
            raise LookupError("检修案例不存在")
        return success(data=CaseService.case_to_dict(repair_case, include_audit_records=True))
    except Exception as exc:
        raise_service_error(exc)


@router.put("/{case_id}", response_model=CaseApiResponse)
def update_case(
    case_id: int,
    payload: RepairCaseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    try:
        repair_case = CaseService.update_case(db, case_id, payload, current_user)
        return success(data=CaseService.case_to_dict(repair_case, include_audit_records=True))
    except Exception as exc:
        raise_service_error(exc)


@router.post("/{case_id}/audit", response_model=CaseApiResponse)
def audit_case(
    case_id: int,
    payload: RepairCaseAudit,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["admin", "auditor"])),
):
    try:
        repair_case = CaseService.audit_case(db, case_id, payload, current_user)
        return success(data=CaseService.case_to_dict(repair_case, include_audit_records=True))
    except Exception as exc:
        raise_service_error(exc)


@router.delete("/{case_id}", response_model=CaseApiResponse)
def delete_case(
    case_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["admin"])),
):
    try:
        CaseService.delete_case(db, case_id)
        return success(data={"case_id": case_id}, message="删除成功")
    except Exception as exc:
        raise_service_error(exc)


@router.get("/{case_id}/audit-records", response_model=CaseApiResponse)
def get_audit_records(
    case_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    try:
        records = CaseService.get_audit_records(db, case_id, current_user)
        return success(data={"items": [CaseService.audit_record_to_dict(record) for record in records]})
    except Exception as exc:
        raise_service_error(exc)
