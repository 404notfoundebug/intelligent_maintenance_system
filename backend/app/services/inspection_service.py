from datetime import datetime
from random import randint

from sqlalchemy import delete, func, or_, select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session, selectinload

from app.models.device import Device
from app.models.inspection import (
    InspectionOrder,
    InspectionOrderStep,
    InspectionTemplate,
    InspectionTemplateStep,
)
from app.models.user import User
from app.schemas.inspection import (
    InspectionOrderCreate,
    InspectionOrderStepUpdate,
    InspectionTemplateCreate,
    InspectionTemplateUpdate,
)


class InspectionService:
    @staticmethod
    def _role_name(user: User) -> str | None:
        return user.role.name if user.role else None

    @staticmethod
    def _ensure_order_access(order: InspectionOrder, user: User) -> None:
        if InspectionService._role_name(user) == "worker" and order.assigned_to != user.id:
            raise PermissionError("没有权限访问该工单")

    @staticmethod
    def _validate_step_orders(steps: list) -> None:
        if not steps:
            raise ValueError("模板步骤不能为空")
        orders = [step.step_order for step in steps]
        if len(orders) != len(set(orders)):
            raise ValueError("模板步骤序号不能重复")

    @staticmethod
    def template_step_to_dict(step: InspectionTemplateStep) -> dict:
        return {
            "id": step.id,
            "template_id": step.template_id,
            "step_order": step.step_order,
            "area": step.area,
            "item_name": step.item_name,
            "item_content": step.item_content,
            "standard": step.standard,
            "required_photo": step.required_photo,
            "required_remark": step.required_remark,
            "created_at": step.created_at,
            "updated_at": step.updated_at,
        }

    @staticmethod
    def template_to_dict(template: InspectionTemplate, include_steps: bool = False) -> dict:
        data = {
            "id": template.id,
            "template_name": template.template_name,
            "device_type": template.device_type,
            "inspection_type": template.inspection_type,
            "description": template.description,
            "is_active": template.is_active,
            "created_by": template.created_by,
            "created_at": template.created_at,
            "updated_at": template.updated_at,
        }
        if include_steps:
            data["steps"] = [InspectionService.template_step_to_dict(step) for step in template.steps]
        return data

    @staticmethod
    def order_step_to_dict(step: InspectionOrderStep) -> dict:
        return {
            "id": step.id,
            "order_id": step.order_id,
            "template_step_id": step.template_step_id,
            "step_order": step.step_order,
            "area": step.area,
            "item_name": step.item_name,
            "item_content": step.item_content,
            "standard": step.standard,
            "result": step.result,
            "remark": step.remark,
            "photo_path": step.photo_path,
            "checked_by": step.checked_by,
            "checked_at": step.checked_at,
            "created_at": step.created_at,
            "updated_at": step.updated_at,
        }

    @staticmethod
    def order_to_dict(order: InspectionOrder, include_steps: bool = False) -> dict:
        data = {
            "id": order.id,
            "order_no": order.order_no,
            "device_id": order.device_id,
            "template_id": order.template_id,
            "order_name": order.order_name,
            "inspection_type": order.inspection_type,
            "status": order.status,
            "assigned_to": order.assigned_to,
            "created_by": order.created_by,
            "started_at": order.started_at,
            "completed_at": order.completed_at,
            "remark": order.remark,
            "created_at": order.created_at,
            "updated_at": order.updated_at,
        }
        if include_steps:
            data["steps"] = [InspectionService.order_step_to_dict(step) for step in order.steps]
        return data

    @staticmethod
    def create_template(db: Session, payload: InspectionTemplateCreate, created_by: int) -> InspectionTemplate:
        InspectionService._validate_step_orders(payload.steps)
        template = InspectionTemplate(
            template_name=payload.template_name,
            device_type=payload.device_type,
            inspection_type=payload.inspection_type,
            description=payload.description,
            is_active=payload.is_active,
            created_by=created_by,
        )
        template.steps = [
            InspectionTemplateStep(
                step_order=step.step_order,
                area=step.area,
                item_name=step.item_name,
                item_content=step.item_content,
                standard=step.standard,
                required_photo=step.required_photo,
                required_remark=step.required_remark,
            )
            for step in sorted(payload.steps, key=lambda item: item.step_order)
        ]

        try:
            db.add(template)
            db.commit()
            db.refresh(template)
            return InspectionService.get_template(db, template.id) or template
        except SQLAlchemyError:
            db.rollback()
            raise

    @staticmethod
    def list_templates(
        db: Session,
        page: int,
        page_size: int,
        device_type: str | None = None,
        inspection_type: str | None = None,
        is_active: bool | None = None,
        keyword: str | None = None,
    ) -> tuple[int, list[InspectionTemplate]]:
        conditions = []
        if device_type:
            conditions.append(InspectionTemplate.device_type == device_type)
        if inspection_type:
            conditions.append(InspectionTemplate.inspection_type == inspection_type)
        if is_active is not None:
            conditions.append(InspectionTemplate.is_active == is_active)
        if keyword:
            pattern = f"%{keyword.strip()}%"
            conditions.append(
                or_(
                    InspectionTemplate.template_name.like(pattern),
                    InspectionTemplate.description.like(pattern),
                )
            )

        count_stmt = select(func.count()).select_from(InspectionTemplate)
        query_stmt = select(InspectionTemplate).order_by(InspectionTemplate.created_at.desc())
        if conditions:
            count_stmt = count_stmt.where(*conditions)
            query_stmt = query_stmt.where(*conditions)

        total = db.scalar(count_stmt) or 0
        items = db.scalars(query_stmt.offset((page - 1) * page_size).limit(page_size)).all()
        return total, list(items)

    @staticmethod
    def get_template(db: Session, template_id: int) -> InspectionTemplate | None:
        stmt = (
            select(InspectionTemplate)
            .options(selectinload(InspectionTemplate.steps))
            .where(InspectionTemplate.id == template_id)
        )
        return db.scalar(stmt)

    @staticmethod
    def update_template(db: Session, template_id: int, payload: InspectionTemplateUpdate) -> InspectionTemplate:
        template = InspectionService.get_template(db, template_id)
        if template is None:
            raise LookupError("点检模板不存在")

        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(template, field, value)

        try:
            db.commit()
            db.refresh(template)
            return InspectionService.get_template(db, template.id) or template
        except SQLAlchemyError:
            db.rollback()
            raise

    @staticmethod
    def delete_or_disable_template(db: Session, template_id: int) -> tuple[InspectionTemplate | None, bool]:
        template = InspectionService.get_template(db, template_id)
        if template is None:
            raise LookupError("点检模板不存在")

        order_count = db.scalar(
            select(func.count()).select_from(InspectionOrder).where(InspectionOrder.template_id == template_id)
        ) or 0
        try:
            if order_count > 0:
                template.is_active = False
                db.commit()
                db.refresh(template)
                return template, True

            db.delete(template)
            db.commit()
            return None, False
        except SQLAlchemyError:
            db.rollback()
            raise

    @staticmethod
    def _generate_order_no(db: Session) -> str:
        for _ in range(10):
            order_no = f"INS{datetime.utcnow().strftime('%Y%m%d%H%M%S')}{randint(100, 999)}"
            exists = db.scalar(select(InspectionOrder.id).where(InspectionOrder.order_no == order_no))
            if exists is None:
                return order_no
        raise RuntimeError("工单编号生成失败，请重试")

    @staticmethod
    def create_order(db: Session, payload: InspectionOrderCreate, current_user: User) -> InspectionOrder:
        device = db.get(Device, payload.device_id)
        if device is None:
            raise LookupError("设备不存在")

        template = InspectionService.get_template(db, payload.template_id)
        if template is None:
            raise LookupError("点检模板不存在")
        if not template.is_active:
            raise ValueError("点检模板未启用")
        if template.device_type != device.device_type:
            raise ValueError("点检模板不适用于该设备类型")
        if not template.steps:
            raise ValueError("点检模板没有步骤，无法生成工单")

        assigned_to = payload.assigned_to
        role_name = InspectionService._role_name(current_user)
        if role_name == "worker":
            if assigned_to is not None and assigned_to != current_user.id:
                raise PermissionError("worker只能创建分配给自己的工单")
            assigned_to = current_user.id
        elif assigned_to is not None and db.get(User, assigned_to) is None:
            raise LookupError("指派用户不存在")

        order = InspectionOrder(
            order_no=InspectionService._generate_order_no(db),
            device_id=device.id,
            template_id=template.id,
            order_name=payload.order_name,
            inspection_type=template.inspection_type,
            status="pending",
            assigned_to=assigned_to,
            created_by=current_user.id,
            remark=payload.remark,
        )
        order.steps = [
            InspectionOrderStep(
                template_step_id=step.id,
                step_order=step.step_order,
                area=step.area,
                item_name=step.item_name,
                item_content=step.item_content,
                standard=step.standard,
                result="unchecked",
            )
            for step in template.steps
        ]

        try:
            db.add(order)
            db.commit()
            db.refresh(order)
            return InspectionService.get_order(db, order.id, current_user) or order
        except IntegrityError as exc:
            db.rollback()
            raise ValueError("工单编号已存在，请重试") from exc
        except SQLAlchemyError:
            db.rollback()
            raise

    @staticmethod
    def list_orders(
        db: Session,
        page: int,
        page_size: int,
        current_user: User,
        device_id: int | None = None,
        status: str | None = None,
        assigned_to: int | None = None,
        keyword: str | None = None,
    ) -> tuple[int, list[InspectionOrder]]:
        conditions = []
        if device_id:
            conditions.append(InspectionOrder.device_id == device_id)
        if status:
            conditions.append(InspectionOrder.status == status)
        if assigned_to:
            conditions.append(InspectionOrder.assigned_to == assigned_to)
        if InspectionService._role_name(current_user) == "worker":
            conditions.append(InspectionOrder.assigned_to == current_user.id)
        if keyword:
            pattern = f"%{keyword.strip()}%"
            conditions.append(
                or_(
                    InspectionOrder.order_no.like(pattern),
                    InspectionOrder.order_name.like(pattern),
                    Device.device_name.like(pattern),
                    Device.device_code.like(pattern),
                )
            )

        count_stmt = select(func.count()).select_from(InspectionOrder).join(Device)
        query_stmt = (
            select(InspectionOrder)
            .join(Device)
            .order_by(InspectionOrder.created_at.desc(), InspectionOrder.id.desc())
        )
        if conditions:
            count_stmt = count_stmt.where(*conditions)
            query_stmt = query_stmt.where(*conditions)

        total = db.scalar(count_stmt) or 0
        items = db.scalars(query_stmt.offset((page - 1) * page_size).limit(page_size)).all()
        return total, list(items)

    @staticmethod
    def get_order(db: Session, order_id: int, current_user: User) -> InspectionOrder | None:
        stmt = (
            select(InspectionOrder)
            .options(selectinload(InspectionOrder.steps))
            .where(InspectionOrder.id == order_id)
        )
        order = db.scalar(stmt)
        if order is not None:
            InspectionService._ensure_order_access(order, current_user)
        return order

    @staticmethod
    def start_order(db: Session, order_id: int, current_user: User) -> InspectionOrder:
        order = InspectionService.get_order(db, order_id, current_user)
        if order is None:
            raise LookupError("点检工单不存在")
        if order.status != "pending":
            raise ValueError("只有pending状态的工单可以开始")

        order.status = "in_progress"
        order.started_at = datetime.utcnow()
        try:
            db.commit()
            db.refresh(order)
            return InspectionService.get_order(db, order.id, current_user) or order
        except SQLAlchemyError:
            db.rollback()
            raise

    @staticmethod
    def update_order_step(
        db: Session,
        order_id: int,
        step_id: int,
        payload: InspectionOrderStepUpdate,
        current_user: User,
    ) -> InspectionOrderStep:
        order = InspectionService.get_order(db, order_id, current_user)
        if order is None:
            raise LookupError("点检工单不存在")
        if order.status != "in_progress":
            raise ValueError("工单未开始，不能填写步骤")

        step = db.scalar(
            select(InspectionOrderStep).where(
                InspectionOrderStep.id == step_id,
                InspectionOrderStep.order_id == order_id,
            )
        )
        if step is None:
            raise LookupError("点检步骤不存在")

        step.result = payload.result
        step.remark = payload.remark
        step.photo_path = payload.photo_path
        step.checked_by = current_user.id
        step.checked_at = datetime.utcnow()

        try:
            db.commit()
            db.refresh(step)
            return step
        except SQLAlchemyError:
            db.rollback()
            raise

    @staticmethod
    def complete_order(db: Session, order_id: int, current_user: User) -> InspectionOrder:
        order = InspectionService.get_order(db, order_id, current_user)
        if order is None:
            raise LookupError("点检工单不存在")
        if order.status != "in_progress":
            raise ValueError("只有in_progress状态的工单可以完成")

        unchecked_count = db.scalar(
            select(func.count())
            .select_from(InspectionOrderStep)
            .where(InspectionOrderStep.order_id == order_id, InspectionOrderStep.result == "unchecked")
        ) or 0
        if unchecked_count > 0:
            raise ValueError(f"仍有未检查项目：{unchecked_count}项")

        order.status = "completed"
        order.completed_at = datetime.utcnow()
        try:
            db.commit()
            db.refresh(order)
            return InspectionService.get_order(db, order.id, current_user) or order
        except SQLAlchemyError:
            db.rollback()
            raise

    @staticmethod
    def delete_order(db: Session, order_id: int) -> None:
        order = db.get(InspectionOrder, order_id)
        if order is None:
            raise LookupError("点检工单不存在")

        try:
            db.execute(delete(InspectionOrderStep).where(InspectionOrderStep.order_id == order_id))
            db.delete(order)
            db.commit()
        except SQLAlchemyError:
            db.rollback()
            raise
