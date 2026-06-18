from datetime import datetime
from random import randint

from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session, selectinload

from app.models.device import Device
from app.models.inspection import InspectionOrder, InspectionOrderStep
from app.models.maintenance import MaintenanceRecord
from app.models.user import User


RESULT_LABELS = {
    "unchecked": "未检查",
    "normal": "正常",
    "abnormal": "异常",
    "not_applicable": "不适用",
}


class MaintenanceService:
    @staticmethod
    def _role_name(user: User) -> str | None:
        return user.role.name if user.role else None

    @staticmethod
    def _ensure_order_access(order: InspectionOrder, user: User) -> None:
        if MaintenanceService._role_name(user) == "worker" and order.assigned_to != user.id:
            raise PermissionError("没有权限访问该工单对应的维保记录")

    @staticmethod
    def _ensure_record_access(db: Session, record: MaintenanceRecord, user: User) -> None:
        if MaintenanceService._role_name(user) != "worker":
            return
        order = db.get(InspectionOrder, record.order_id)
        if order is None or order.assigned_to != user.id:
            raise PermissionError("没有权限访问该维保记录")

    @staticmethod
    def _generate_record_no(db: Session) -> str:
        for _ in range(10):
            record_no = f"MR{datetime.utcnow().strftime('%Y%m%d%H%M%S')}{randint(100, 999)}"
            exists = db.scalar(select(MaintenanceRecord.id).where(MaintenanceRecord.record_no == record_no))
            if exists is None:
                return record_no
        raise RuntimeError("维保记录编号生成失败，请重试")

    @staticmethod
    def to_dict(record: MaintenanceRecord, include_report: bool = True) -> dict:
        data = {
            "id": record.id,
            "record_no": record.record_no,
            "order_id": record.order_id,
            "device_id": record.device_id,
            "device_name": record.device_name,
            "device_code": record.device_code,
            "device_type": record.device_type,
            "maintenance_company": record.maintenance_company,
            "responsible_person": record.responsible_person,
            "inspection_type": record.inspection_type,
            "order_no": record.order_no,
            "start_time": record.start_time,
            "end_time": record.end_time,
            "total_items": record.total_items,
            "normal_items": record.normal_items,
            "abnormal_items": record.abnormal_items,
            "not_applicable_items": record.not_applicable_items,
            "conclusion": record.conclusion,
            "audit_status": record.audit_status,
            "auditor_id": record.auditor_id,
            "audit_time": record.audit_time,
            "reject_reason": record.reject_reason,
            "generated_by": record.generated_by,
            "created_at": record.created_at,
            "updated_at": record.updated_at,
        }
        if include_report:
            data["report_content"] = record.report_content
        return data

    @staticmethod
    def _format_time(value: datetime | None) -> str:
        if value is None:
            return "未记录"
        return value.strftime("%Y-%m-%d %H:%M:%S")

    @staticmethod
    def _build_report_content(
        device: Device,
        order: InspectionOrder,
        steps: list[InspectionOrderStep],
        total_items: int,
        normal_items: int,
        abnormal_items: int,
        not_applicable_items: int,
        conclusion: str,
        executor_name: str,
    ) -> str:
        detail_lines = []
        abnormal_lines = []
        for index, step in enumerate(sorted(steps, key=lambda item: item.step_order), start=1):
            result_label = RESULT_LABELS.get(step.result, step.result)
            remark = step.remark or "无"
            detail_lines.append(
                f"{index}. 检查区域：{step.area}\n"
                f"   检查项目：{step.item_name}\n"
                f"   检查内容：{step.item_content}\n"
                f"   检查标准：{step.standard or '未填写'}\n"
                f"   检查结果：{result_label}\n"
                f"   备注：{remark}"
            )
            if step.result == "abnormal":
                abnormal_lines.append(f"- {step.area} / {step.item_name}：{remark}")

        abnormal_summary = "\n".join(abnormal_lines) if abnormal_lines else "本次点检未发现异常项目。"
        details = "\n\n".join(detail_lines) if detail_lines else "无点检明细。"

        return f"""《电梯/扶梯维保自检报告》

一、设备基本信息
设备名称：{device.device_name}
设备编号：{device.device_code}
设备类型：{device.device_type}
安装位置：{device.installation_location or "未填写"}
维保单位：{device.maintenance_company or "未填写"}

二、点检工单信息
工单编号：{order.order_no}
点检类型：{order.inspection_type}
开始时间：{MaintenanceService._format_time(order.started_at)}
完成时间：{MaintenanceService._format_time(order.completed_at)}
执行人员：{executor_name}

三、点检项目统计
点检项目总数：{total_items}
正常项目：{normal_items}
异常项目：{abnormal_items}
不适用项目：{not_applicable_items}

四、点检明细
{details}

五、异常项目汇总
{abnormal_summary}

六、维保结论
{conclusion}

七、安全提示
电梯/扶梯属于特种设备，检修和维保应由具备资质的专业人员执行。系统生成内容仅作为维保记录整理与辅助参考，最终结果应由现场维保人员确认。

生成时间：{MaintenanceService._format_time(datetime.utcnow())}"""

    @staticmethod
    def _get_order_with_steps(db: Session, order_id: int) -> InspectionOrder | None:
        stmt = (
            select(InspectionOrder)
            .options(selectinload(InspectionOrder.steps))
            .where(InspectionOrder.id == order_id)
        )
        return db.scalar(stmt)

    @staticmethod
    def generate_record_from_order(
        db: Session,
        order_id: int,
        current_user: User,
    ) -> tuple[MaintenanceRecord, bool]:
        order = MaintenanceService._get_order_with_steps(db, order_id)
        if order is None:
            raise LookupError("点检工单不存在")
        MaintenanceService._ensure_order_access(order, current_user)

        existing = db.scalar(select(MaintenanceRecord).where(MaintenanceRecord.order_id == order_id))
        if existing is not None:
            MaintenanceService._ensure_record_access(db, existing, current_user)
            return existing, True

        if order.status != "completed":
            raise ValueError("工单未完成，不能生成维保记录")

        device = db.get(Device, order.device_id)
        if device is None:
            raise LookupError("设备不存在")

        steps = list(order.steps)
        total_items = len(steps)
        normal_items = sum(1 for step in steps if step.result == "normal")
        abnormal_items = sum(1 for step in steps if step.result == "abnormal")
        not_applicable_items = sum(1 for step in steps if step.result == "not_applicable")
        conclusion = (
            "存在异常项目，建议进一步复核处理"
            if abnormal_items > 0
            else "本次点检项目未发现明显异常"
        )

        executor = db.get(User, order.assigned_to) if order.assigned_to else None
        executor_name = (executor.real_name or executor.username) if executor else "未指派"
        report_content = MaintenanceService._build_report_content(
            device=device,
            order=order,
            steps=steps,
            total_items=total_items,
            normal_items=normal_items,
            abnormal_items=abnormal_items,
            not_applicable_items=not_applicable_items,
            conclusion=conclusion,
            executor_name=executor_name,
        )

        record = MaintenanceRecord(
            record_no=MaintenanceService._generate_record_no(db),
            order_id=order.id,
            device_id=device.id,
            device_name=device.device_name,
            device_code=device.device_code,
            device_type=device.device_type,
            maintenance_company=device.maintenance_company,
            responsible_person=device.responsible_person,
            inspection_type=order.inspection_type,
            order_no=order.order_no,
            start_time=order.started_at,
            end_time=order.completed_at,
            total_items=total_items,
            normal_items=normal_items,
            abnormal_items=abnormal_items,
            not_applicable_items=not_applicable_items,
            conclusion=conclusion,
            report_content=report_content,
            generated_by=current_user.id,
        )

        try:
            db.add(record)
            db.commit()
            db.refresh(record)
            return record, False
        except IntegrityError as exc:
            db.rollback()
            existing = db.scalar(select(MaintenanceRecord).where(MaintenanceRecord.order_id == order_id))
            if existing is not None:
                return existing, True
            raise ValueError("维保记录编号或工单记录已存在，请重试") from exc
        except SQLAlchemyError:
            db.rollback()
            raise

    @staticmethod
    def list_records(
        db: Session,
        page: int,
        page_size: int,
        current_user: User,
        keyword: str | None = None,
        device_id: int | None = None,
        inspection_type: str | None = None,
    ) -> tuple[int, list[MaintenanceRecord]]:
        conditions = []
        if keyword:
            pattern = f"%{keyword.strip()}%"
            conditions.append(
                or_(
                    MaintenanceRecord.record_no.like(pattern),
                    MaintenanceRecord.device_name.like(pattern),
                    MaintenanceRecord.device_code.like(pattern),
                )
            )
        if device_id:
            conditions.append(MaintenanceRecord.device_id == device_id)
        if inspection_type:
            conditions.append(MaintenanceRecord.inspection_type == inspection_type)

        count_stmt = select(func.count()).select_from(MaintenanceRecord)
        query_stmt = select(MaintenanceRecord).order_by(MaintenanceRecord.created_at.desc(), MaintenanceRecord.id.desc())

        if MaintenanceService._role_name(current_user) == "worker":
            count_stmt = count_stmt.join(InspectionOrder, MaintenanceRecord.order_id == InspectionOrder.id)
            query_stmt = query_stmt.join(InspectionOrder, MaintenanceRecord.order_id == InspectionOrder.id)
            conditions.append(InspectionOrder.assigned_to == current_user.id)

        if conditions:
            count_stmt = count_stmt.where(*conditions)
            query_stmt = query_stmt.where(*conditions)

        total = db.scalar(count_stmt) or 0
        items = db.scalars(query_stmt.offset((page - 1) * page_size).limit(page_size)).all()
        return total, list(items)

    @staticmethod
    def get_record(db: Session, record_id: int, current_user: User) -> MaintenanceRecord | None:
        record = db.get(MaintenanceRecord, record_id)
        if record is not None:
            MaintenanceService._ensure_record_access(db, record, current_user)
        return record

    @staticmethod
    def get_report(db: Session, record_id: int, current_user: User) -> dict:
        record = MaintenanceService.get_record(db, record_id, current_user)
        if record is None:
            raise LookupError("维保记录不存在")
        return {
            "record_id": record.id,
            "record_no": record.record_no,
            "report_content": record.report_content,
        }

    @staticmethod
    def delete_record(db: Session, record_id: int) -> None:
        record = db.get(MaintenanceRecord, record_id)
        if record is None:
            raise LookupError("维保记录不存在")
        try:
            db.delete(record)
            db.commit()
        except SQLAlchemyError:
            db.rollback()
            raise

    @staticmethod
    def audit_record(
        db: Session,
        record_id: int,
        status: str,
        current_user: User,
        reject_reason: str | None = None,
    ) -> MaintenanceRecord:
        record = db.get(MaintenanceRecord, record_id)
        if record is None:
            raise LookupError("维保记录不存在")
        if status not in ("approved", "rejected"):
            raise ValueError("审核状态无效，必须为 approved 或 rejected")
        if status == "rejected" and not reject_reason:
            raise ValueError("驳回时必须提供驳回原因")
        if record.audit_status != "pending":
            raise ValueError("该记录已审核，无法重复操作")

        record.audit_status = status
        record.auditor_id = current_user.id
        record.audit_time = datetime.utcnow()
        record.reject_reason = reject_reason if status == "rejected" else None

        try:
            db.commit()
            db.refresh(record)
            return record
        except SQLAlchemyError:
            db.rollback()
            raise
