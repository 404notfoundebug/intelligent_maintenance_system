from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Device(Base):
    __tablename__ = "devices"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    device_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    device_code: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    device_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    device_model: Mapped[str | None] = mapped_column(String(100), nullable=True)
    manufacturer: Mapped[str | None] = mapped_column(String(100), nullable=True)
    installation_location: Mapped[str | None] = mapped_column(String(200), nullable=True, index=True)
    maintenance_company: Mapped[str | None] = mapped_column(String(100), nullable=True)
    responsible_person: Mapped[str | None] = mapped_column(String(50), nullable=True)
    contact_phone: Mapped[str | None] = mapped_column(String(32), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="normal", nullable=False, index=True)
    remark: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    creator = relationship("User")
