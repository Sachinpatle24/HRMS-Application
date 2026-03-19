from datetime import datetime, timezone
from sqlalchemy import ForeignKey, String, Float, Text, DateTime, Integer, BigInteger, Boolean, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.core.config import settings


class Resume(Base):
    __tablename__ = settings.RESUME_TABLE_NAME
    __table_args__ = {"extend_existing": True}

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        nullable=False
    )

    # Personal Details
    name: Mapped[str] = mapped_column(String(), nullable=True)
    email: Mapped[str] = mapped_column(String(), nullable=True)
    phone: Mapped[str] = mapped_column(String(), nullable=True)
    alternate_number: Mapped[str | None] = mapped_column(String(), nullable=True)
    website: Mapped[str | None] = mapped_column(Text, nullable=True)
    date_of_birth: Mapped[str | None] = mapped_column(String(), nullable=True)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Resume content
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    education: Mapped[str] = mapped_column(Text, nullable=True)
    work_experience: Mapped[str | None] = mapped_column(Text, nullable=True)
    skills: Mapped[str | None] = mapped_column(Text, nullable=True)
    certifications: Mapped[str | None] = mapped_column(Text, nullable=True)
    projects: Mapped[str | None] = mapped_column(Text, nullable=True)

    # File metadata
    file_name: Mapped[str | None] = mapped_column(String(), nullable=True, comment="Original uploaded filename for traceability only")

    # Computed fields
    total_experience: Mapped[float | None] = mapped_column(Float, nullable=True)
    total_experience_pretty: Mapped[str | None] = mapped_column(String(), nullable=True)
    experience_per_company: Mapped[str | None] = mapped_column(Text, nullable=True)
    experience_per_company_pretty: Mapped[str | None] = mapped_column(Text, nullable=True)

    # User-only fields
    current_company: Mapped[str | None] = mapped_column(String(), nullable=True)
    designation: Mapped[str | None] = mapped_column(String(), nullable=True)
    last_working_day: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), 
        nullable=True
    )
    notice_period: Mapped[int | None] = mapped_column(Integer, nullable=True)
    

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

    active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )

    is_complete: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )

    created_by: Mapped[int] = mapped_column(
        BigInteger, 
        ForeignKey(f"{settings.USER_TABLE_NAME}.id"),
        nullable=False
    )

    attachment = relationship(
        "Attachment",
        back_populates="resume",
        uselist=False,
        # cascade="all, delete-orphan"
        passive_deletes=True
    )

    raw_data = relationship(
        "CandidateRawData",
        back_populates="resume",
        uselist=False,
        # cascade="all, delete-orphan",
        passive_deletes=True
    )

    audit_logs = relationship(
        "ResumeAuditLog",
        back_populates="resume",
        uselist=True,
        # cascade="all, delete-orphan",
        passive_deletes=True
        
    )

    interviews = relationship(
        "Interview",
        back_populates="candidate",
        uselist=True, 
        passive_deletes=True
    )
    
    def __repr__(self) -> str:
        return f"<Resume(id={self.id}, name={self.name}, email={self.email})>"