from datetime import datetime
from random import randint

from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session, selectinload

from app.models.case import CaseAuditRecord, RepairCase
from app.models.device import Device
from app.models.fault import FaultReport
from app.models.knowledge import KnowledgeChunk
from app.models.maintenance import MaintenanceRecord
from app.models.user import User
from app.schemas.case import RepairCaseAudit, RepairCaseCreate, RepairCaseUpdate


class CaseService:
    @staticmethod
    def _role_name(user: User) -> str | None:
        return user.role.name if user.role else None

    @staticmethod
    def _ensure_case_access(repair_case: RepairCase, user: User) -> None:
        if CaseService._role_name(user) == "worker" and repair_case.submitted_by != user.id:
            raise PermissionError("没有权限访问该检修案例")

    @staticmethod
    def _generate_case_no(db: Session) -> str:
        for _ in range(10):
            case_no = f"RC{datetime.utcnow().strftime('%Y%m%d%H%M%S')}{randint(100, 999)}"
            exists = db.scalar(select(RepairCase.id).where(RepairCase.case_no == case_no))
            if exists is None:
                return case_no
        raise RuntimeError("案例编号生成失败，请重试")

    @staticmethod
    def audit_record_to_dict(record: CaseAuditRecord) -> dict:
        return {
            "id": record.id,
            "case_id": record.case_id,
            "action": record.action,
            "comment": record.comment,
            "operator_id": record.operator_id,
            "created_at": record.created_at,
            "updated_at": record.updated_at,
        }

    @staticmethod
    def case_to_dict(repair_case: RepairCase, include_audit_records: bool = False) -> dict:
        data = {
            "id": repair_case.id,
            "case_no": repair_case.case_no,
            "device_id": repair_case.device_id,
            "fault_report_id": repair_case.fault_report_id,
            "maintenance_record_id": repair_case.maintenance_record_id,
            "title": repair_case.title,
            "device_name": repair_case.device_name,
            "device_type": repair_case.device_type,
            "fault_description": repair_case.fault_description,
            "fault_reason": repair_case.fault_reason,
            "repair_process": repair_case.repair_process,
            "repair_result": repair_case.repair_result,
            "tools_used": repair_case.tools_used,
            "safety_notes": repair_case.safety_notes,
            "status": repair_case.status,
            "submitted_by": repair_case.submitted_by,
            "reviewed_by": repair_case.reviewed_by,
            "reviewed_at": repair_case.reviewed_at,
            "review_comment": repair_case.review_comment,
            "knowledge_chunk_id": repair_case.knowledge_chunk_id,
            "created_at": repair_case.created_at,
            "updated_at": repair_case.updated_at,
        }
        if include_audit_records:
            data["audit_records"] = [
                CaseService.audit_record_to_dict(record) for record in repair_case.audit_records
            ]
        return data

    @staticmethod
    def _validate_references(
        db: Session,
        device_id: int | None = None,
        fault_report_id: int | None = None,
        maintenance_record_id: int | None = None,
    ) -> Device | None:
        device = None
        if device_id:
            device = db.get(Device, device_id)
            if device is None:
                raise LookupError("设备不存在")
        if fault_report_id and db.get(FaultReport, fault_report_id) is None:
            raise LookupError("故障记录不存在")
        if maintenance_record_id and db.get(MaintenanceRecord, maintenance_record_id) is None:
            raise LookupError("维保记录不存在")
        return device

    @staticmethod
    def create_case(db: Session, payload: RepairCaseCreate, current_user: User) -> RepairCase:
        device = CaseService._validate_references(
            db,
            device_id=payload.device_id,
            fault_report_id=payload.fault_report_id,
            maintenance_record_id=payload.maintenance_record_id,
        )
        repair_case = RepairCase(
            case_no=CaseService._generate_case_no(db),
            device_id=payload.device_id,
            fault_report_id=payload.fault_report_id,
            maintenance_record_id=payload.maintenance_record_id,
            title=payload.title,
            device_name=payload.device_name or (device.device_name if device else None),
            device_type=payload.device_type or (device.device_type if device else None),
            fault_description=payload.fault_description,
            fault_reason=payload.fault_reason,
            repair_process=payload.repair_process,
            repair_result=payload.repair_result,
            tools_used=payload.tools_used,
            safety_notes=payload.safety_notes,
            status="pending",
            submitted_by=current_user.id,
        )
        repair_case.audit_records = [
            CaseAuditRecord(
                action="submit",
                comment="提交检修案例",
                operator_id=current_user.id,
            )
        ]
        try:
            db.add(repair_case)
            db.commit()
            db.refresh(repair_case)
            return CaseService.get_case(db, repair_case.id, current_user) or repair_case
        except IntegrityError as exc:
            db.rollback()
            raise ValueError("案例编号已存在，请重试") from exc
        except SQLAlchemyError:
            db.rollback()
            raise

    @staticmethod
    def list_cases(
        db: Session,
        page: int,
        page_size: int,
        current_user: User,
        keyword: str | None = None,
        status: str | None = None,
        device_id: int | None = None,
        submitted_by: int | None = None,
    ) -> tuple[int, list[RepairCase]]:
        conditions = []
        if keyword:
            pattern = f"%{keyword.strip()}%"
            conditions.append(
                or_(
                    RepairCase.title.like(pattern),
                    RepairCase.fault_description.like(pattern),
                    RepairCase.device_name.like(pattern),
                )
            )
        if status:
            conditions.append(RepairCase.status == status)
        if device_id:
            conditions.append(RepairCase.device_id == device_id)
        if submitted_by:
            conditions.append(RepairCase.submitted_by == submitted_by)
        if CaseService._role_name(current_user) == "worker":
            conditions.append(RepairCase.submitted_by == current_user.id)

        count_stmt = select(func.count()).select_from(RepairCase)
        query_stmt = select(RepairCase).order_by(RepairCase.created_at.desc(), RepairCase.id.desc())
        if conditions:
            count_stmt = count_stmt.where(*conditions)
            query_stmt = query_stmt.where(*conditions)

        total = db.scalar(count_stmt) or 0
        items = db.scalars(query_stmt.offset((page - 1) * page_size).limit(page_size)).all()
        return total, list(items)

    @staticmethod
    def get_case(db: Session, case_id: int, current_user: User) -> RepairCase | None:
        stmt = (
            select(RepairCase)
            .options(selectinload(RepairCase.audit_records))
            .where(RepairCase.id == case_id)
        )
        repair_case = db.scalar(stmt)
        if repair_case is not None:
            CaseService._ensure_case_access(repair_case, current_user)
        return repair_case

    @staticmethod
    def update_case(db: Session, case_id: int, payload: RepairCaseUpdate, current_user: User) -> RepairCase:
        repair_case = CaseService.get_case(db, case_id, current_user)
        if repair_case is None:
            raise LookupError("检修案例不存在")

        role_name = CaseService._role_name(current_user)
        if role_name == "worker" and repair_case.status == "approved":
            raise PermissionError("已审核通过的案例不允许worker修改")

        update_data = payload.model_dump(exclude_unset=True)
        CaseService._validate_references(
            db,
            device_id=update_data.get("device_id"),
            fault_report_id=update_data.get("fault_report_id"),
            maintenance_record_id=update_data.get("maintenance_record_id"),
        )
        for field, value in update_data.items():
            setattr(repair_case, field, value)

        if repair_case.status in {"draft", "rejected"}:
            repair_case.status = "pending"
            repair_case.audit_records.append(
                CaseAuditRecord(action="submit", comment="修改后重新提交", operator_id=current_user.id)
            )

        try:
            db.commit()
            db.refresh(repair_case)
            return CaseService.get_case(db, repair_case.id, current_user) or repair_case
        except SQLAlchemyError:
            db.rollback()
            raise

    @staticmethod
    def _build_case_content(repair_case: RepairCase) -> str:
        return f"""【检修案例】
案例标题：{repair_case.title}
案例编号：{repair_case.case_no}
设备名称：{repair_case.device_name or "未填写"}
设备类型：{repair_case.device_type or "未填写"}
故障现象：{repair_case.fault_description}
故障原因：{repair_case.fault_reason}
检修过程：{repair_case.repair_process}
处理结果：{repair_case.repair_result}
使用工具：{repair_case.tools_used or "未填写"}
安全注意事项：{repair_case.safety_notes or "未填写"}"""

    @staticmethod
    def approve_case_to_knowledge(db: Session, repair_case: RepairCase) -> KnowledgeChunk:
        if repair_case.knowledge_chunk_id:
            existing_chunk = db.get(KnowledgeChunk, repair_case.knowledge_chunk_id)
            if existing_chunk is not None:
                existing_chunk.title = repair_case.title
                existing_chunk.content = CaseService._build_case_content(repair_case)
                existing_chunk.metadata_json = {
                    "source": "repair_case",
                    "document_type": "fault_case",
                    "case_id": repair_case.id,
                    "case_no": repair_case.case_no,
                }
                return existing_chunk

        chunk = KnowledgeChunk(
            file_id=None,
            chunk_index=0,
            title=repair_case.title,
            content=CaseService._build_case_content(repair_case),
            metadata_json={
                "source": "repair_case",
                "document_type": "fault_case",
                "case_id": repair_case.id,
                "case_no": repair_case.case_no,
            },
        )
        db.add(chunk)
        db.flush()
        repair_case.knowledge_chunk_id = chunk.id
        return chunk

    @staticmethod
    def audit_case(db: Session, case_id: int, payload: RepairCaseAudit, current_user: User) -> RepairCase:
        repair_case = CaseService.get_case(db, case_id, current_user)
        if repair_case is None:
            raise LookupError("检修案例不存在")

        if payload.action == "approve":
            repair_case.status = "approved"
            CaseService.approve_case_to_knowledge(db, repair_case)
        elif payload.action == "reject":
            repair_case.status = "rejected"
        elif payload.action == "return":
            repair_case.status = "draft"

        repair_case.reviewed_by = current_user.id
        repair_case.reviewed_at = datetime.utcnow()
        repair_case.review_comment = payload.comment
        repair_case.audit_records.append(
            CaseAuditRecord(
                action=payload.action,
                comment=payload.comment,
                operator_id=current_user.id,
            )
        )

        try:
            db.commit()
            db.refresh(repair_case)
            return CaseService.get_case(db, repair_case.id, current_user) or repair_case
        except SQLAlchemyError:
            db.rollback()
            raise

    @staticmethod
    def delete_case(db: Session, case_id: int) -> None:
        repair_case = db.get(RepairCase, case_id)
        if repair_case is None:
            raise LookupError("检修案例不存在")
        try:
            db.delete(repair_case)
            db.commit()
        except SQLAlchemyError:
            db.rollback()
            raise

    @staticmethod
    def get_audit_records(db: Session, case_id: int, current_user: User) -> list[CaseAuditRecord]:
        repair_case = CaseService.get_case(db, case_id, current_user)
        if repair_case is None:
            raise LookupError("检修案例不存在")
        return list(repair_case.audit_records)
