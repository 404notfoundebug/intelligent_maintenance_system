from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class InspectionTemplate(Base):
    __tablename__ = "inspection_templates"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    template_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    device_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    inspection_type: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    creator = relationship("User")
    steps: Mapped[list["InspectionTemplateStep"]] = relationship(
        back_populates="template",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="InspectionTemplateStep.step_order",
    )
    orders: Mapped[list["InspectionOrder"]] = relationship(back_populates="template")


class InspectionTemplateStep(Base):
    __tablename__ = "inspection_template_steps"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    template_id: Mapped[int] = mapped_column(
        ForeignKey("inspection_templates.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    step_order: Mapped[int] = mapped_column(Integer, nullable=False)
    area: Mapped[str] = mapped_column(String(100), nullable=False)
    item_name: Mapped[str] = mapped_column(String(100), nullable=False)
    item_content: Mapped[str] = mapped_column(Text, nullable=False)
    standard: Mapped[str | None] = mapped_column(Text, nullable=True)
    required_photo: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    required_remark: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    template: Mapped[InspectionTemplate] = relationship(back_populates="steps")


class InspectionOrder(Base):
    __tablename__ = "inspection_orders"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    order_no: Mapped[str] = mapped_column(String(32), unique=True, nullable=False, index=True)
    device_id: Mapped[int] = mapped_column(ForeignKey("devices.id"), nullable=False, index=True)
    template_id: Mapped[int] = mapped_column(ForeignKey("inspection_templates.id"), nullable=False, index=True)
    order_name: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    inspection_type: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(20), default="pending", nullable=False, index=True)
    assigned_to: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    remark: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    device = relationship("Device")
    template: Mapped[InspectionTemplate] = relationship(back_populates="orders")
    assignee = relationship("User", foreign_keys=[assigned_to])
    creator = relationship("User", foreign_keys=[created_by])
    steps: Mapped[list["InspectionOrderStep"]] = relationship(
        back_populates="order",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="InspectionOrderStep.step_order",
    )


class InspectionOrderStep(Base):
    __tablename__ = "inspection_order_steps"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    order_id: Mapped[int] = mapped_column(
        ForeignKey("inspection_orders.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    template_step_id: Mapped[int | None] = mapped_column(
        ForeignKey("inspection_template_steps.id"),
        nullable=True,
        index=True,
    )
    step_order: Mapped[int] = mapped_column(Integer, nullable=False)
    area: Mapped[str] = mapped_column(String(100), nullable=False)
    item_name: Mapped[str] = mapped_column(String(100), nullable=False)
    item_content: Mapped[str] = mapped_column(Text, nullable=False)
    standard: Mapped[str | None] = mapped_column(Text, nullable=True)
    result: Mapped[str] = mapped_column(String(20), default="unchecked", nullable=False, index=True)
    remark: Mapped[str | None] = mapped_column(Text, nullable=True)
    photo_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    checked_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)
    checked_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    order: Mapped[InspectionOrder] = relationship(back_populates="steps")
    template_step = relationship("InspectionTemplateStep")
    checker = relationship("User")
