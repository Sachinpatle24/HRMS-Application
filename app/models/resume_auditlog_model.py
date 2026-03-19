from datetime import datetime, timezone
from sqlalchemy import String, ForeignKey, Text, DateTime, BigInteger, Boolean, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.core.config import settings


class ResumeAuditLog(Base):
    __tablename__ = settings.RESUME_AUDITLOG_TABLE_NAME
    __table_args__ = {"extend_existing": True}

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        nullable=False
    )

    candidate_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(f"{settings.RESUME_TABLE_NAME}.id", ondelete="CASCADE"),
        nullable=True,
    )
    
    file_name: Mapped[str] = mapped_column(String(), nullable=False)

    resume_status: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    free_text: Mapped[str | None] = mapped_column(Text, nullable=True)  

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("SYSUTCDATETIME()"),
        nullable=False
    )

    resume = relationship("Resume", back_populates="audit_logs")
