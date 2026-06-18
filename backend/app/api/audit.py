from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.api.auth import get_current_active_user, require_roles
from app.core.database import get_db
from app.models.user import User
from app.services.audit_service import AuditService

router = APIRouter(prefix="/api/audit-logs", tags=["audit"])


def success(data: dict | list | None = None, message: str = "success") -> dict:
    return {"code": 200, "message": message, "data": data or {}}


@router.get("")
def list_audit_logs(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    module: str | None = None,
    action: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["admin"])),
):
    try:
        total, items = AuditService.list_logs(
            db, page=page, page_size=page_size, module=module, action=action,
        )
        return success(data={
            "total": total,
            "page": page,
            "page_size": page_size,
            "items": [AuditService.to_dict(item) for item in items],
        })
    except SQLAlchemyError as exc:
        return {"code": 500, "message": f"数据库操作失败：{exc}", "data": {}}
