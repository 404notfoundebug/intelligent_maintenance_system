import shutil
import logging
from datetime import datetime
from pathlib import Path
from random import randint
from uuid import uuid4

from fastapi import UploadFile
from sqlalchemy import delete, func, or_, select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session, selectinload

from app.core.config import settings
from app.models.device import Device
from app.models.fault import FaultImage, FaultReport
from app.models.user import User
from app.schemas.fault import FaultReportCreate, FaultReportUpdateStatus, IMAGE_TYPES
from app.services.qa_service import QAService
from app.services.vision_client import VisionClient

logger = logging.getLogger(__name__)


SUPPORTED_IMAGE_TYPES = {"jpg", "jpeg", "png", "webp"}

VISION_PROMPT = """请识别这张电梯/扶梯维保现场图片，重点关注：
1. 是否存在可见故障码或报警信息
2. 图片中可能涉及的部件
3. 是否存在明显异常现象
4. 对维保人员的安全提醒
5. 输出结构化文字结果"""


class FaultService:
    @staticmethod
    def _role_name(user: User) -> str | None:
        return user.role.name if user.role else None

    @staticmethod
    def _ensure_fault_access(fault_report: FaultReport, user: User) -> None:
        if FaultService._role_name(user) == "worker" and fault_report.submitted_by != user.id:
            raise PermissionError("没有权限访问该故障记录")

    @staticmethod
    def _generate_report_no(db: Session) -> str:
        for _ in range(10):
            report_no = f"FR{datetime.utcnow().strftime('%Y%m%d%H%M%S')}{randint(100, 999)}"
            exists = db.scalar(select(FaultReport.id).where(FaultReport.report_no == report_no))
            if exists is None:
                return report_no
        raise RuntimeError("故障上报编号生成失败，请重试")

    @staticmethod
    def image_to_dict(image: FaultImage) -> dict:
        return {
            "id": image.id,
            "fault_report_id": image.fault_report_id,
            "original_filename": image.original_filename,
            "stored_filename": image.stored_filename,
            "file_path": image.file_path,
            "file_type": image.file_type,
            "image_type": image.image_type,
            "file_size": image.file_size,
            "vision_status": image.vision_status,
            "vision_result": image.vision_result,
            "vision_error": image.vision_error,
            "uploaded_by": image.uploaded_by,
            "created_at": image.created_at,
            "updated_at": image.updated_at,
        }

    @staticmethod
    def report_to_dict(fault_report: FaultReport, include_images: bool = False) -> dict:
        data = {
            "id": fault_report.id,
            "report_no": fault_report.report_no,
            "device_id": fault_report.device_id,
            "device_name": fault_report.device_name,
            "device_model": fault_report.device_model,
            "fault_description": fault_report.fault_description,
            "fault_code": fault_report.fault_code,
            "location": fault_report.location,
            "status": fault_report.status,
            "submitted_by": fault_report.submitted_by,
            "advice_record_id": fault_report.advice_record_id,
            "created_at": fault_report.created_at,
            "updated_at": fault_report.updated_at,
        }
        if include_images:
            data["images"] = [FaultService.image_to_dict(image) for image in fault_report.images]
        return data

    @staticmethod
    def create_fault_report(db: Session, payload: FaultReportCreate, current_user: User) -> FaultReport:
        device = None
        if payload.device_id:
            device = db.get(Device, payload.device_id)
            if device is None:
                raise LookupError("设备不存在")

        fault_report = FaultReport(
            report_no=FaultService._generate_report_no(db),
            device_id=payload.device_id,
            device_name=payload.device_name or (device.device_name if device else None),
            device_model=payload.device_model or (device.device_model if device else None),
            fault_description=payload.fault_description,
            fault_code=payload.fault_code,
            location=payload.location or (device.installation_location if device else None),
            status="pending",
            submitted_by=current_user.id,
        )
        try:
            db.add(fault_report)
            db.commit()
            db.refresh(fault_report)
            return fault_report
        except IntegrityError as exc:
            db.rollback()
            raise ValueError("故障上报编号已存在，请重试") from exc
        except SQLAlchemyError:
            db.rollback()
            raise

    @staticmethod
    def get_fault_report(db: Session, fault_id: int, current_user: User) -> FaultReport | None:
        stmt = (
            select(FaultReport)
            .options(selectinload(FaultReport.images))
            .where(FaultReport.id == fault_id)
        )
        fault_report = db.scalar(stmt)
        if fault_report is not None:
            FaultService._ensure_fault_access(fault_report, current_user)
        return fault_report

    @staticmethod
    def list_fault_reports(
        db: Session,
        page: int,
        page_size: int,
        current_user: User,
        keyword: str | None = None,
        device_id: int | None = None,
        status: str | None = None,
    ) -> tuple[int, list[FaultReport]]:
        conditions = []
        if keyword:
            pattern = f"%{keyword.strip()}%"
            conditions.append(
                or_(
                    FaultReport.report_no.like(pattern),
                    FaultReport.device_name.like(pattern),
                    FaultReport.fault_description.like(pattern),
                )
            )
        if device_id:
            conditions.append(FaultReport.device_id == device_id)
        if status:
            conditions.append(FaultReport.status == status)
        if FaultService._role_name(current_user) == "worker":
            conditions.append(FaultReport.submitted_by == current_user.id)

        count_stmt = select(func.count()).select_from(FaultReport)
        query_stmt = select(FaultReport).order_by(FaultReport.created_at.desc(), FaultReport.id.desc())
        if conditions:
            count_stmt = count_stmt.where(*conditions)
            query_stmt = query_stmt.where(*conditions)

        total = db.scalar(count_stmt) or 0
        items = db.scalars(query_stmt.offset((page - 1) * page_size).limit(page_size)).all()
        return total, list(items)

    @staticmethod
    def update_fault_status(
        db: Session,
        fault_id: int,
        payload: FaultReportUpdateStatus,
        current_user: User,
    ) -> FaultReport:
        fault_report = FaultService.get_fault_report(db, fault_id, current_user)
        if fault_report is None:
            raise LookupError("故障记录不存在")

        fault_report.status = payload.status
        try:
            db.commit()
            db.refresh(fault_report)
            return FaultService.get_fault_report(db, fault_id, current_user) or fault_report
        except SQLAlchemyError:
            db.rollback()
            raise

    @staticmethod
    def _save_uploaded_image(file: UploadFile) -> tuple[Path, str, str, int]:
        original_filename = Path(file.filename or "").name
        file_type = Path(original_filename).suffix.lower().lstrip(".")
        if file_type not in SUPPORTED_IMAGE_TYPES:
            raise ValueError("仅支持jpg、jpeg、png、webp图片")

        upload_dir = Path(settings.upload_dir) / "fault_images"
        upload_dir.mkdir(parents=True, exist_ok=True)
        stored_filename = f"{uuid4().hex}.{file_type}"
        saved_path = upload_dir / stored_filename

        try:
            with saved_path.open("wb") as target:
                shutil.copyfileobj(file.file, target)
        except OSError as exc:
            raise RuntimeError(f"图片保存失败：{exc}") from exc
        finally:
            file.file.close()

        return saved_path, stored_filename, file_type, saved_path.stat().st_size

    @staticmethod
    def upload_fault_image(
        db: Session,
        fault_id: int,
        file: UploadFile,
        image_type: str,
        current_user: User,
    ) -> FaultImage:
        if image_type not in IMAGE_TYPES:
            raise ValueError("不支持的图片类型")

        fault_report = FaultService.get_fault_report(db, fault_id, current_user)
        if fault_report is None:
            raise LookupError("故障记录不存在")

        original_filename = Path(file.filename or "").name
        saved_path, stored_filename, file_type, file_size = FaultService._save_uploaded_image(file)
        image = FaultImage(
            fault_report_id=fault_report.id,
            original_filename=original_filename,
            stored_filename=stored_filename,
            file_path=saved_path.as_posix(),
            file_type=file_type,
            image_type=image_type,
            file_size=file_size,
            vision_status="pending",
            uploaded_by=current_user.id,
        )
        try:
            db.add(image)
            db.commit()
            db.refresh(image)
            return image
        except SQLAlchemyError:
            db.rollback()
            try:
                if saved_path.exists() and saved_path.is_file():
                    saved_path.unlink()
            except OSError:
                logger.warning("清理故障图片文件失败: %s", saved_path)
            raise

    @staticmethod
    def _get_fault_image(db: Session, fault_id: int, image_id: int, current_user: User) -> tuple[FaultReport, FaultImage]:
        fault_report = FaultService.get_fault_report(db, fault_id, current_user)
        if fault_report is None:
            raise LookupError("故障记录不存在")
        image = db.scalar(
            select(FaultImage).where(
                FaultImage.id == image_id,
                FaultImage.fault_report_id == fault_id,
            )
        )
        if image is None:
            raise LookupError("故障图片不存在")
        return fault_report, image

    @staticmethod
    def analyze_fault_image(db: Session, fault_id: int, image_id: int, current_user: User) -> FaultImage:
        fault_report, image = FaultService._get_fault_image(db, fault_id, image_id, current_user)
        fault_report.status = "analyzing"
        image.vision_status = "pending"
        image.vision_error = None
        try:
            db.commit()
        except SQLAlchemyError:
            db.rollback()
            raise

        try:
            result = VisionClient().analyze_image(image.file_path, VISION_PROMPT)
            image.vision_status = "success"
            image.vision_result = result
            image.vision_error = None
            db.commit()
            db.refresh(image)
            return image
        except Exception as exc:
            db.rollback()
            image = db.get(FaultImage, image_id)
            if image is not None:
                image.vision_status = "failed"
                image.vision_error = str(exc)
                try:
                    db.commit()
                    db.refresh(image)
                except SQLAlchemyError:
                    db.rollback()
            raise RuntimeError(str(exc)) from exc

    @staticmethod
    def _build_enhanced_fault_description(fault_report: FaultReport) -> str:
        parts = [f"故障现象：{fault_report.fault_description}"]
        if fault_report.fault_code:
            parts.append(f"故障码：{fault_report.fault_code}")
        if fault_report.location:
            parts.append(f"故障位置：{fault_report.location}")

        vision_results = [
            f"[图片{index}] 类型：{image.image_type}\n识别结果：{image.vision_result}"
            for index, image in enumerate(fault_report.images, start=1)
            if image.vision_status == "success" and image.vision_result
        ]
        if vision_results:
            parts.append("图片识别结果：\n" + "\n\n".join(vision_results))
        return "\n\n".join(parts)

    @staticmethod
    def generate_repair_advice_from_fault(
        db: Session,
        fault_id: int,
        current_user: User,
        top_k: int = 5,
    ) -> tuple[FaultReport, object, list[dict]]:
        fault_report = FaultService.get_fault_report(db, fault_id, current_user)
        if fault_report is None:
            raise LookupError("故障记录不存在")

        enhanced_description = FaultService._build_enhanced_fault_description(fault_report)
        qa_record, references = QAService.generate_repair_advice(
            db=db,
            user_id=current_user.id,
            device_name=fault_report.device_name,
            device_model=fault_report.device_model,
            fault_description=enhanced_description,
            top_k=top_k,
        )
        fault_report.advice_record_id = qa_record.id
        fault_report.status = "advised"
        try:
            db.commit()
            db.refresh(fault_report)
            return fault_report, qa_record, references
        except SQLAlchemyError:
            db.rollback()
            raise

    @staticmethod
    def delete_fault_report(db: Session, fault_id: int) -> None:
        stmt = select(FaultReport).options(selectinload(FaultReport.images)).where(FaultReport.id == fault_id)
        fault_report = db.scalar(stmt)
        if fault_report is None:
            raise LookupError("故障记录不存在")

        image_paths = [Path(image.file_path) for image in fault_report.images]
        try:
            db.execute(delete(FaultImage).where(FaultImage.fault_report_id == fault_id))
            db.delete(fault_report)
            db.commit()
        except SQLAlchemyError:
            db.rollback()
            raise

        for image_path in image_paths:
            try:
                if image_path.exists() and image_path.is_file():
                    image_path.unlink()
            except OSError:
                logger.warning("删除故障图片文件失败: %s", image_path)
