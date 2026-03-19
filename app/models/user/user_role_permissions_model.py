from datetime import datetime
from sqlalchemy import BigInteger, ForeignKey, DateTime, Boolean, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.core.config import settings


class UserRolePermission(Base):
    __tablename__ = settings.USER_ROLE_PERMISSION_TABLE_NAME
    __table_args__ = {"extend_existing": True}

    id: Mapped[int] = mapped_column(
        BigInteger, 
        primary_key=True,
        nullable=False
    )

    role_id: Mapped[int] = mapped_column(
        BigInteger, 
        ForeignKey(f"{settings.USER_ROLE_TABLE_NAME}.id"), 
        nullable=False
    )

    menu_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(f"{settings.MENU_MASTER_TABLE_NAME}.id"), 
        nullable=False
    )

    is_editable: Mapped[bool] = mapped_column(Boolean, nullable=False)

    is_view: Mapped[bool] = mapped_column(Boolean, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, 
        server_default=text("SYSUTCDATETIME()"), 
        nullable=False
    )

    role = relationship("UserRole", back_populates="permissions")
    menu = relationship("MenuMaster", uselist=False)

    def __repr__(self) -> str:
        return (
            f"<UserRolePermission id={self.id} "
            f"role_id={self.role_id} menu_id={self.menu_id}>"
        )
