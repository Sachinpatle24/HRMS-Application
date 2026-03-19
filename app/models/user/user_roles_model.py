from sqlalchemy import BigInteger, String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.core.config import settings


class UserRole(Base):
    __tablename__ = settings.USER_ROLE_TABLE_NAME
    __table_args__ = {"extend_existing": True}

    id: Mapped[int] = mapped_column(
        BigInteger, 
        primary_key=True,
        nullable=False
    )

    role_name: Mapped[str] = mapped_column(String(), nullable=False)
    description: Mapped[str | None] = mapped_column(String(), nullable=True)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    users = relationship("User", back_populates="user_role")
    permissions = relationship("UserRolePermission", back_populates="role")


    def __repr__(self) -> str:
        return f"<UserRole id={self.id} role_name={self.role_name}>"
