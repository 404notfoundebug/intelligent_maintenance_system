from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import select, func, desc

from app.models.audit import AuditLog
from app.models.user import User


class AuditService:

    @staticmethod
    def write(
        db: Session,
        action: str,
        module: str,
        target_type: str,
        target_id: int | None = None,
        target_name: str | None = None,
        detail: str | None = None,
        operator: User | None = None,
        ip_address: str | None = None,
    ) -> AuditLog:
        entry = AuditLog(
            action=action,
            module=module,
            target_type=target_type,
            target_id=target_id,
            target_name=target_name,
            detail=detail,
            operator_id=operator.id if operator else None,
            operator_name=operator.username if operator else None,
            ip_address=ip_address,
        )
        try:
            db.add(entry)
            db.commit()
            db.refresh(entry)
            return entry
        except SQLAlchemyError:
            db.rollback()
            raise

    @staticmethod
    def list_logs(
        db: Session,
        page: int = 1,
        page_size: int = 20,
        module: str | None = None,
        action: str | None = None,
        operator_id: int | None = None,
    ) -> tuple[int, list[AuditLog]]:
        stmt = select(AuditLog)
        count_stmt = select(func.count()).select_from(AuditLog)

        if module:
            stmt = stmt.where(AuditLog.module == module)
            count_stmt = count_stmt.where(AuditLog.module == module)
        if action:
            stmt = stmt.where(AuditLog.action == action)
            count_stmt = count_stmt.where(AuditLog.action == action)
        if operator_id is not None:
            stmt = stmt.where(AuditLog.operator_id == operator_id)
            count_stmt = count_stmt.where(AuditLog.operator_id == operator_id)

        total = db.scalar(count_stmt) or 0
        offset = (page - 1) * page_size
        stmt = stmt.order_by(desc(AuditLog.created_at)).offset(offset).limit(page_size)
        items = list(db.scalars(stmt).all())
        return total, items

    @staticmethod
    def to_dict(log: AuditLog) -> dict:
        return {
            "id": log.id,
            "action": log.action,
            "module": log.module,
            "target_type": log.target_type,
            "target_id": log.target_id,
            "target_name": log.target_name,
            "detail": log.detail,
            "operator_id": log.operator_id,
            "operator_name": log.operator_name,
            "ip_address": log.ip_address,
            "created_at": log.created_at.isoformat() if log.created_at else None,
        }
