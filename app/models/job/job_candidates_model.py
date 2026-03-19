from datetime import datetime
from sqlalchemy import BigInteger, String, DateTime, ForeignKey, Boolean, text
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base
from app.core.config import settings


class JobCandidate(Base):
    __tablename__ = settings.JOB_CANDIDATE_TABLE_NAME
    __table_args__ = {"extend_existing": True}
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    job_id: Mapped[int] = mapped_column(BigInteger, ForeignKey(f"{settings.JOB_TABLE_NAME}.id"), nullable=False)
    candidate_id: Mapped[int] = mapped_column(BigInteger, ForeignKey(f"{settings.RESUME_TABLE_NAME}.id"), nullable=False)
    current_stage_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(f"{settings.DROPDOWN_TABLE_NAME}.id"),
        nullable=True
    )
    current_result_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(f"{settings.DROPDOWN_TABLE_NAME}.id"),
        nullable=True
    )
    created: Mapped[datetime] = mapped_column(DateTime, server_default=text("SYSUTCDATETIME()"), nullable=False)
    updated: Mapped[datetime] = mapped_column(DateTime, server_default=text("SYSUTCDATETIME()"), nullable=False)
    created_by: Mapped[int] = mapped_column(BigInteger, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, server_default=text("1"), nullable=False)
    status: Mapped[str] = mapped_column(String(50), server_default=text("'Applied'"), nullable=False)
