# app/models/candidate_raw_data_model.py
from datetime import datetime, timezone
from sqlalchemy import Text, ForeignKey, DateTime, BigInteger, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.core.config import settings

class CandidateRawData(Base):
    __tablename__ = settings.CANDIDATE_RAW_DATA_TABLE_NAME
    __table_args__ = {"extend_existing": True}

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        nullable=False,
    )

    candidate_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(f"{settings.RESUME_TABLE_NAME}.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )

    raw_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    parsed_json: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("SYSUTCDATETIME()"),
        nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("SYSUTCDATETIME()"),
        nullable=False
    )

    resume = relationship("Resume", back_populates="raw_data")
