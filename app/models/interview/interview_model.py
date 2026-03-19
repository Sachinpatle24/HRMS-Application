from datetime import datetime, date, time
from sqlalchemy import Date, Time, DateTime
from sqlalchemy import String, Text, BigInteger, Boolean, ForeignKey, LargeBinary, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.core.config import settings


class Interview(Base):
    __tablename__ = settings.INTERVIEW_TABLE_NAME
    __table_args__ = {"extend_existing": True}

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        nullable=False
    )

    job_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey(f"{settings.JOB_TABLE_NAME}.id", ondelete="SET NULL"),
        nullable=False
    )
    
    job_candidate_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey(f"{settings.JOB_CANDIDATE_TABLE_NAME}.id", ondelete="SET NULL"),
        nullable=False
    )

    candidate_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(f"{settings.RESUME_TABLE_NAME}.id", ondelete="CASCADE"),
        nullable=False
    )
    
    scheduled_interview_date: Mapped[date] = mapped_column(Date, nullable=False)
    scheduled_start_time: Mapped[time] = mapped_column(Time, nullable=False)
    scheduled_end_time: Mapped[time | None] = mapped_column(Time, nullable=True)
    
    duration_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    stage_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    
    interviewer_id: Mapped[str] = mapped_column(String(), nullable=False)
    is_interviewer_external: Mapped[bool] = mapped_column(Boolean, nullable=False)
    interviewer_name: Mapped[str | None] = mapped_column(String(), nullable=True)
    interviewer_email_id: Mapped[str | None] = mapped_column(String(), nullable=True)
    
    interview_mode_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey(f"{settings.DROPDOWN_TABLE_NAME}.id"),
        nullable=True
    )
    location: Mapped[str | None] = mapped_column(String(), nullable=True)
    video_call_link: Mapped[str | None] = mapped_column(String(), nullable=True)

    additional_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    comments: Mapped[str | None] = mapped_column(Text, nullable=True)
    upload_feedback_template: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)
    feedback_filename: Mapped[str | None] = mapped_column(String(), nullable=True)


    rating_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey(f"{settings.DROPDOWN_TABLE_NAME}.id"),
        nullable=True
    )
    result_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey(f"{settings.DROPDOWN_TABLE_NAME}.id"),
        nullable=True
    )
    rejection_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey(f"{settings.DROPDOWN_TABLE_NAME}.id"),
        nullable=True
    )

    active: Mapped[bool] = mapped_column(Boolean, server_default=text("1"))
    status: Mapped[str] = mapped_column(String(), nullable=False)
    created_by: Mapped[int] = mapped_column(
        BigInteger, 
        ForeignKey(f"{settings.USER_TABLE_NAME}.id"),
        nullable=False
    )


    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("SYSUTCDATETIME()"),
        nullable=False
    )
    feedback_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("SYSUTCDATETIME()"),
        nullable=False
    )

    # Relationships
    candidate = relationship(
        "Resume",
        back_populates="interviews",
    )

    job = relationship(
        "Job",
        back_populates="interviews",
    )

    rating = relationship(
        "MasterDropdown",
        foreign_keys=[rating_id],
        uselist=False
    )

    result = relationship(
        "MasterDropdown",
        foreign_keys=[result_id],
        uselist=False
    )

    def __repr__(self) -> str:
        return f"<Interview(id={self.id}, candidate_id={self.candidate_id}, rating_id={self.rating_id})>"
