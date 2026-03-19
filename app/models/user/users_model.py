from datetime import datetime
from sqlalchemy import BigInteger, String, ForeignKey, DateTime, Boolean, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.core.config import settings


class User(Base):
    __tablename__ = settings.USER_TABLE_NAME
    __table_args__ = {"extend_existing": True}

    id: Mapped[int] = mapped_column(
        BigInteger, 
        primary_key=True, 
        nullable=False
    )

    employee_code: Mapped[str] = mapped_column(String(), nullable=False)
    username: Mapped[str] = mapped_column(String(), nullable=False)
    email: Mapped[str] = mapped_column(String(), nullable=False)
    full_name: Mapped[str] = mapped_column(String(), nullable=False)

    user_role_id: Mapped[int] = mapped_column(
        BigInteger, 
        ForeignKey(f"{settings.USER_ROLE_TABLE_NAME}.id"), 
        nullable=False
    )

    parent_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey(f"{settings.USER_TABLE_NAME}.id"), nullable=True)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=text("SYSUTCDATETIME()"), nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=text("SYSUTCDATETIME()"),
        nullable=False
    )

    user_role = relationship("UserRole", back_populates="users")

    def __repr__(self) -> str:
        return f"<User id={self.id} username={self.username}>"
