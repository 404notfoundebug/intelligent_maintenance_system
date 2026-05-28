from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class FaultReport(Base):
    __tablename__ = "fault_reports"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    report_no: Mapped[str] = mapped_column(String(32), unique=True, nullable=False, index=True)
    device_id: Mapped[int | None] = mapped_column(ForeignKey("devices.id"), nullable=True, index=True)
    device_name: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    device_model: Mapped[str | None] = mapped_column(String(100), nullable=True)
    fault_description: Mapped[str] = mapped_column(Text, nullable=False)
    fault_code: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    location: Mapped[str | None] = mapped_column(String(200), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="pending", nullable=False, index=True)
    submitted_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    advice_record_id: Mapped[int | None] = mapped_column(ForeignKey("qa_records.id"), nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    device = relationship("Device")
    submitter = relationship("User")
    advice_record = relationship("QARecord")
    images: Mapped[list["FaultImage"]] = relationship(
        back_populates="fault_report",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="FaultImage.created_at",
    )


class FaultImage(Base):
    __tablename__ = "fault_images"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    fault_report_id: Mapped[int] = mapped_column(
        ForeignKey("fault_reports.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    stored_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    file_type: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    image_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    vision_status: Mapped[str] = mapped_column(String(20), default="pending", nullable=False, index=True)
    vision_result: Mapped[str | None] = mapped_column(Text, nullable=True)
    vision_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    uploaded_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    fault_report: Mapped[FaultReport] = relationship(back_populates="images")
    uploader = relationship("User")
