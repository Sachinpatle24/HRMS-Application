# app/models/attachment_model.py
from datetime import datetime, timezone
from sqlalchemy import String, LargeBinary, ForeignKey, DateTime, BigInteger, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.core.config import settings

class Attachment(Base):
    __tablename__ = settings.ATTACHMENT_TABLE_NAME
    __table_args__ = {"extend_existing": True}

    # Primary Key
    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        nullable=False, 
    )

    # Foreign Key to Resume
    candidate_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(f"{settings.RESUME_TABLE_NAME}.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )

    # File metadata
    file_name: Mapped[str | None] = mapped_column(String(), nullable=True)
    file_data: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)
    file_type: Mapped[str | None] = mapped_column(String(), nullable=True)

    status: Mapped[str] = mapped_column(String(), default="active", nullable=False)
    
    # Timezone-aware timestamps
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

    resume = relationship(
        "Resume", 
        back_populates="attachment"
    )

