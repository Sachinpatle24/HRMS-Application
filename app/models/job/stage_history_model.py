from datetime import datetime
from sqlalchemy import BigInteger, String, DateTime, ForeignKey, text
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base
from app.core.config import settings


class StageHistory(Base):
    __tablename__ = "stage_history"
    __table_args__ = {"extend_existing": True}

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, nullable=False)
    job_candidate_id: Mapped[int] = mapped_column(BigInteger, ForeignKey(f"{settings.JOB_CANDIDATE_TABLE_NAME}.id", ondelete="CASCADE"), nullable=False)
    from_stage_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    to_stage_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    from_result_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    to_result_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    changed_by: Mapped[int] = mapped_column(BigInteger, ForeignKey(f"{settings.USER_TABLE_NAME}.id"), nullable=False)
    changed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("SYSUTCDATETIME()"), nullable=False)
