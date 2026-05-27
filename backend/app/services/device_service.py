from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.device import Device
from app.schemas.device import DeviceCreate, DeviceUpdate


class DeviceService:
    @staticmethod
    def to_dict(device: Device) -> dict:
        return {
            "id": device.id,
            "device_name": device.device_name,
            "device_code": device.device_code,
            "device_type": device.device_type,
            "device_model": device.device_model,
            "manufacturer": device.manufacturer,
            "installation_location": device.installation_location,
            "maintenance_company": device.maintenance_company,
            "responsible_person": device.responsible_person,
            "contact_phone": device.contact_phone,
            "status": device.status,
            "remark": device.remark,
            "created_by": device.created_by,
            "created_at": device.created_at,
            "updated_at": device.updated_at,
        }

    @staticmethod
    def get_by_id(db: Session, device_id: int) -> Device | None:
        return db.get(Device, device_id)

    @staticmethod
    def get_by_code(db: Session, device_code: str) -> Device | None:
        return db.scalar(select(Device).where(Device.device_code == device_code))

    @staticmethod
    def create_device(db: Session, payload: DeviceCreate, created_by: int) -> Device:
        if DeviceService.get_by_code(db, payload.device_code):
            raise ValueError("设备编号已存在")

        device = Device(
            **payload.model_dump(),
            created_by=created_by,
        )
        try:
            db.add(device)
            db.commit()
            db.refresh(device)
            return device
        except IntegrityError as exc:
            db.rollback()
            raise ValueError("设备编号已存在") from exc
        except SQLAlchemyError:
            db.rollback()
            raise

    @staticmethod
    def list_devices(
        db: Session,
        page: int,
        page_size: int,
        keyword: str | None = None,
        device_type: str | None = None,
        status: str | None = None,
    ) -> tuple[int, list[Device]]:
        conditions = []
        if keyword:
            pattern = f"%{keyword.strip()}%"
            conditions.append(
                or_(
                    Device.device_name.like(pattern),
                    Device.device_code.like(pattern),
                    Device.installation_location.like(pattern),
                )
            )
        if device_type:
            conditions.append(Device.device_type == device_type)
        if status:
            conditions.append(Device.status == status)

        count_stmt = select(func.count()).select_from(Device)
        query_stmt = select(Device).order_by(Device.created_at.desc(), Device.id.desc())
        if conditions:
            count_stmt = count_stmt.where(*conditions)
            query_stmt = query_stmt.where(*conditions)

        total = db.scalar(count_stmt) or 0
        items = db.scalars(query_stmt.offset((page - 1) * page_size).limit(page_size)).all()
        return total, list(items)

    @staticmethod
    def update_device(db: Session, device_id: int, payload: DeviceUpdate) -> Device:
        device = DeviceService.get_by_id(db, device_id)
        if device is None:
            raise LookupError("设备不存在")

        update_data = payload.model_dump(exclude_unset=True)
        new_device_code = update_data.get("device_code")
        if new_device_code and new_device_code != device.device_code:
            existing = DeviceService.get_by_code(db, new_device_code)
            if existing and existing.id != device.id:
                raise ValueError("设备编号已存在")

        for field, value in update_data.items():
            setattr(device, field, value)

        try:
            db.commit()
            db.refresh(device)
            return device
        except IntegrityError as exc:
            db.rollback()
            raise ValueError("设备编号已存在") from exc
        except SQLAlchemyError:
            db.rollback()
            raise

    @staticmethod
    def delete_device(db: Session, device_id: int) -> None:
        device = DeviceService.get_by_id(db, device_id)
        if device is None:
            raise LookupError("设备不存在")

        try:
            db.delete(device)
            db.commit()
        except SQLAlchemyError:
            db.rollback()
            raise
