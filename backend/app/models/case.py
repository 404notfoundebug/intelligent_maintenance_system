from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class RepairCase(Base):
    __tablename__ = "repair_cases"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    case_no: Mapped[str] = mapped_column(String(32), unique=True, nullable=False, index=True)
    device_id: Mapped[int | None] = mapped_column(ForeignKey("devices.id"), nullable=True, index=True)
    fault_report_id: Mapped[int | None] = mapped_column(ForeignKey("fault_reports.id"), nullable=True, index=True)
    maintenance_record_id: Mapped[int | None] = mapped_column(
        ForeignKey("maintenance_records.id"),
        nullable=True,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    device_name: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    device_type: Mapped[str | None] = mapped_column(String(50), nullable=True, index=True)
    fault_description: Mapped[str] = mapped_column(Text, nullable=False)
    fault_reason: Mapped[str] = mapped_column(Text, nullable=False)
    repair_process: Mapped[str] = mapped_column(Text, nullable=False)
    repair_result: Mapped[str] = mapped_column(Text, nullable=False)
    tools_used: Mapped[str | None] = mapped_column(Text, nullable=True)
    safety_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="pending", nullable=False, index=True)
    submitted_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    reviewed_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    review_comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    knowledge_chunk_id: Mapped[int | None] = mapped_column(ForeignKey("knowledge_chunks.id"), nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    device = relationship("Device")
    fault_report = relationship("FaultReport")
    maintenance_record = relationship("MaintenanceRecord")
    submitter = relationship("User", foreign_keys=[submitted_by])
    reviewer = relationship("User", foreign_keys=[reviewed_by])
    knowledge_chunk = relationship("KnowledgeChunk")
    audit_records: Mapped[list["CaseAuditRecord"]] = relationship(
        back_populates="repair_case",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="CaseAuditRecord.created_at",
    )


class CaseAuditRecord(Base):
    __tablename__ = "case_audit_records"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    case_id: Mapped[int] = mapped_column(
        ForeignKey("repair_cases.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    action: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    operator_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    repair_case: Mapped[RepairCase] = relationship(back_populates="audit_records")
    operator = relationship("User")
