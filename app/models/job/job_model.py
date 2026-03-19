from datetime import datetime, timezone
from sqlalchemy import String, Text, DateTime, BigInteger, ForeignKey, Integer, Boolean, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.core.config import settings
 
 
class Job(Base):
    __tablename__ = settings.JOB_TABLE_NAME
    __table_args__ = {"extend_existing": True}
   
    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        nullable=False
    )
   
    title: Mapped[str] = mapped_column()
    number_of_positions: Mapped[int] = mapped_column(Integer)
    
    mandatory_skills: Mapped[str | None] = mapped_column(Text, nullable=True)
    desired_skills: Mapped[str | None] = mapped_column(Text, nullable=True)
    qualification: Mapped[str | None] = mapped_column(Text, nullable=True)
   
    location: Mapped[str | None] = mapped_column(nullable=True)
    experience_level: Mapped[str | None] = mapped_column(nullable=True)
 
    job_description: Mapped[str | None] = mapped_column(Text, nullable=True)
   
    status_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey(f"{settings.DROPDOWN_TABLE_NAME}.id"),
        nullable=True
    )
    
    department: Mapped[str | None] = mapped_column(nullable=True)
    positions_filled: Mapped[int] = mapped_column(Integer, default=0)
   
    created: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("SYSUTCDATETIME()"),
        nullable=False
    )
    updated: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("SYSUTCDATETIME()"),
        nullable=False
    )
    created_by: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(f"{settings.USER_TABLE_NAME}.id"),
        nullable=False
    )

    assigned_to: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey(f"{settings.USER_TABLE_NAME}.id"),
        nullable=True
    )
 
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    interviews = relationship(
        "Interview",
        back_populates="job",
        uselist=True,
        passive_deletes=True
    )

    status = relationship(
        "MasterDropdown",
        foreign_keys=[status_id],
        uselist=False
    )

    created_by_user = relationship(
        "User",
        foreign_keys=[created_by],
        uselist=False
    )

    assigned_to_user = relationship(
        "User",
        foreign_keys=[assigned_to],
        uselist=False
    )
