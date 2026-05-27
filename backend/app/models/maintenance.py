from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class MaintenanceRecord(Base):
    __tablename__ = "maintenance_records"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    record_no: Mapped[str] = mapped_column(String(32), unique=True, nullable=False, index=True)
    order_id: Mapped[int] = mapped_column(
        ForeignKey("inspection_orders.id"),
        unique=True,
        nullable=False,
        index=True,
    )
    device_id: Mapped[int] = mapped_column(ForeignKey("devices.id"), nullable=False, index=True)
    device_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    device_code: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    device_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    maintenance_company: Mapped[str | None] = mapped_column(String(100), nullable=True)
    responsible_person: Mapped[str | None] = mapped_column(String(50), nullable=True)
    inspection_type: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    order_no: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    start_time: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    end_time: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    total_items: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    normal_items: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    abnormal_items: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    not_applicable_items: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    conclusion: Mapped[str] = mapped_column(String(255), nullable=False)
    report_content: Mapped[str] = mapped_column(Text, nullable=False)
    generated_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    order = relationship("InspectionOrder")
    device = relationship("Device")
    generator = relationship("User")
